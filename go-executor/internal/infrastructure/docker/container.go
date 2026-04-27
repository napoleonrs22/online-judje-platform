package docker

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"time"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/pkg/stdcopy"
)

// runResult - результат выполнения контейнера на низком уровне
type runResult struct {
	Stdout     string
	Stderr     string
	ExitCode   int
	Duration   time.Duration
	MemoryUsed int64 // В байтах
	Timeout    bool
	OOMKilled  bool
}

// localStats - Локальная структура для чтения статистики.
type localStats struct {
	MemoryStats struct {
		Usage uint64 `json:"usage"`
	} `json:"memory_stats"`
}

// runContainer запускает изолированный контейнер.
//
// Если workDirCopy не пустой, содержимое этой папки на хосте (внутри code-executor)
// упаковывается в tar и загружается в /app через CopyToContainer — без bind-mount к демону
// Docker (это ломалось на Docker Desktop / Windows).
//
// Если workDirCopy пустой и bindPath не пустой — используется старый режим bind (только для совместимости).
//
// afterSuccess вызывается после успешного завершения (exit 0, без TLE/OOM), до удаления контейнера —
// например, чтобы забрать скомпилированный бинарник из /app.
func (d *DockerExecutor) runContainer(
	ctx context.Context,
	image string,
	cmd []string,
	bindPath string,
	workDirCopy string,
	env []string,
	timeLimitMS int,
	memLimitMB int,
	stdin []byte,
	afterSuccess func(ctx context.Context, containerID string) error,
) (runResult, error) {

	pidsLimit := int64(64)
	memoryLimitBytes := int64(memLimitMB) * 1024 * 1024

	resources := container.Resources{
		Memory:     memoryLimitBytes,
		MemorySwap: memoryLimitBytes,
		NanoCPUs:   1000000000,
		PidsLimit:  &pidsLimit,
	}

	useStdin := len(stdin) > 0
	config := &container.Config{
		Image:           image,
		Cmd:             cmd,
		Env:             env,
		WorkingDir:      "/app",
		NetworkDisabled: true,
		Tty:             false,
		OpenStdin:       useStdin,
		StdinOnce:       useStdin,
		AttachStdin:     useStdin,
	}
	if useStdin {
		config.AttachStdout = true
		config.AttachStderr = true
	}

	hostConfig := &container.HostConfig{
		Resources:   resources,
		NetworkMode: "none",
	}
	if workDirCopy == "" && bindPath != "" {
		hostConfig.Binds = []string{fmt.Sprintf("%s:/app", bindPath)}
	}

	resp, err := d.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, "")
	if err != nil {
		return runResult{}, fmt.Errorf("failed to create container: %w", err)
	}
	containerID := resp.ID

	defer func() {
		removeOpts := container.RemoveOptions{
			Force:         true,
			RemoveVolumes: true,
		}
		_ = d.cli.ContainerRemove(context.Background(), containerID, removeOpts)
	}()

	if workDirCopy != "" {
		tarR, err := tarDirectoryFlatReader(workDirCopy)
		if err != nil {
			return runResult{}, fmt.Errorf("tar workdir: %w", err)
		}
		err = d.cli.CopyToContainer(ctx, containerID, "/app", tarR, container.CopyToContainerOptions{})
		if err != nil {
			return runResult{}, fmt.Errorf("copy to container: %w", err)
		}
	}

	maxMemCh := make(chan int64, 1)
	go memoryMonitor(containerID, d, timeLimitMS, maxMemCh)

	startTime := time.Now()

	var result runResult

	if useStdin {
		attach, err := d.cli.ContainerAttach(ctx, containerID, container.AttachOptions{
			Stream: true,
			Stdin:  true,
			Stdout: true,
			Stderr: true,
		})
		if err != nil {
			return runResult{}, fmt.Errorf("failed to attach container: %w", err)
		}
		defer attach.Close()

		if err := d.cli.ContainerStart(ctx, containerID, container.StartOptions{}); err != nil {
			return runResult{}, fmt.Errorf("failed to start container: %w", err)
		}

		go func() {
			defer attach.CloseWrite()
			_, _ = io.Copy(attach.Conn, bytes.NewReader(stdin))
		}()

		var outBuf, errBuf bytes.Buffer
		copyDone := make(chan struct{})
		go func() {
			_, _ = stdcopy.StdCopy(&outBuf, &errBuf, attach.Reader)
			close(copyDone)
		}()

		result, err = waitContainer(ctx, d, containerID, timeLimitMS, startTime)
		if err != nil {
			return result, err
		}

		<-copyDone
		result.Stdout = outBuf.String()
		result.Stderr = errBuf.String()
	} else {
		if err := d.cli.ContainerStart(ctx, containerID, container.StartOptions{}); err != nil {
			return runResult{}, fmt.Errorf("failed to start container: %w", err)
		}

		result, err = waitContainer(ctx, d, containerID, timeLimitMS, startTime)
		if err != nil {
			return result, err
		}

		outReader, err := d.cli.ContainerLogs(context.Background(), containerID, container.LogsOptions{
			ShowStdout: true,
			ShowStderr: true,
		})
		if err == nil {
			defer outReader.Close()
			var outBuf, errBuf bytes.Buffer
			_, _ = stdcopy.StdCopy(&outBuf, &errBuf, io.LimitReader(outReader, 512*1024))
			result.Stdout = outBuf.String()
			result.Stderr = errBuf.String()
		}
	}

	select {
	case mem := <-maxMemCh:
		result.MemoryUsed = mem
	case <-time.After(100 * time.Millisecond):
	}

	if afterSuccess != nil && result.ExitCode == 0 && !result.Timeout && !result.OOMKilled {
		if err := afterSuccess(ctx, containerID); err != nil {
			return result, fmt.Errorf("after container success: %w", err)
		}
	}

	return result, nil
}

func memoryMonitor(containerID string, d *DockerExecutor, timeLimitMS int, maxMemCh chan int64) {
	var maxUsage int64 = 0
	ticker := time.NewTicker(50 * time.Millisecond)
	defer ticker.Stop()

	timeoutMonitor := time.NewTimer(time.Duration(timeLimitMS+2000) * time.Millisecond)
	defer timeoutMonitor.Stop()

	for {
		select {
		case <-timeoutMonitor.C:
			maxMemCh <- maxUsage
			return
		case <-ticker.C:
			stats, err := d.cli.ContainerStats(context.Background(), containerID, false)
			if err != nil {
				maxMemCh <- maxUsage
				return
			}

			var v localStats
			if err := json.NewDecoder(stats.Body).Decode(&v); err == nil {
				usage := int64(v.MemoryStats.Usage)
				if usage > maxUsage {
					maxUsage = usage
				}
			}
			stats.Body.Close()
		}
	}
}

func waitContainer(
	ctx context.Context,
	d *DockerExecutor,
	containerID string,
	timeLimitMS int,
	startTime time.Time,
) (runResult, error) {
	waitCh, errCh := d.cli.ContainerWait(ctx, containerID, container.WaitConditionNotRunning)
	timeoutDuration := time.Duration(timeLimitMS) * time.Millisecond
	ctxTimeout, cancel := context.WithTimeout(ctx, timeoutDuration)
	defer cancel()

	result := runResult{}

	select {
	case err := <-errCh:
		return result, fmt.Errorf("error waiting for container: %w", err)
	case <-ctxTimeout.Done():
		result.Timeout = true
		_ = d.cli.ContainerKill(context.Background(), containerID, "SIGKILL")
	case waitResp := <-waitCh:
		result.ExitCode = int(waitResp.StatusCode)
		if result.ExitCode == 137 {
			result.OOMKilled = true
		}
	}

	result.Duration = time.Since(startTime)
	return result, nil
}
