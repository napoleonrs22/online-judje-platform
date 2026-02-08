package docker

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"time"

	// Удалили api/types, так как используем localStats
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
// Мы используем её вместо types.StatsJSON, чтобы избежать проблем с версиями зависимостей.
type localStats struct {
	MemoryStats struct {
		Usage uint64 `json:"usage"`
	} `json:"memory_stats"`
}

// runContainer - Универсальная функция запуска изолированного контейнера
func (d *DockerExecutor) runContainer(
	ctx context.Context,
	image string,
	cmd []string,
	bindPath string,
	env []string,
	timeLimitMS int,
	memLimitMB int,
) (runResult, error) {

	pidsLimit := int64(64)
	memoryLimitBytes := int64(memLimitMB) * 1024 * 1024

	resources := container.Resources{
		Memory:     memoryLimitBytes,
		MemorySwap: memoryLimitBytes,
		NanoCPUs:   1000000000,
		PidsLimit:  &pidsLimit,
	}

	config := &container.Config{
		Image:           image,
		Cmd:             cmd,
		Env:             env,
		WorkingDir:      "/app",
		NetworkDisabled: true,
		Tty:             false,
		OpenStdin:       false,
	}

	hostConfig := &container.HostConfig{
		Binds:       []string{fmt.Sprintf("%s:/app", bindPath)},
		Resources:   resources,
		NetworkMode: "none",
	}

	// 1. Создание
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

	// 2. Запуск
	startTime := time.Now()
	if err := d.cli.ContainerStart(ctx, containerID, container.StartOptions{}); err != nil {
		return runResult{}, fmt.Errorf("failed to start container: %w", err)
	}

	// 3. Мониторинг памяти
	maxMemCh := make(chan int64, 1)
	go func() {
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

				// ИСПОЛЬЗУЕМ ЛОКАЛЬНУЮ СТРУКТУРУ localStats
				// Это гарантирует, что код скомпилируется, какая бы версия Docker SDK ни стояла.
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
	}()

	// 4. Ожидание
	waitCh, errCh := d.cli.ContainerWait(ctx, containerID, container.WaitConditionNotRunning)
	timeoutDuration := time.Duration(timeLimitMS) * time.Millisecond
	ctxTimeout, cancel := context.WithTimeout(ctx, timeoutDuration)
	defer cancel()

	result := runResult{}

	select {
	case err := <-errCh:
		return runResult{}, fmt.Errorf("error waiting for container: %w", err)
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

	select {
	case mem := <-maxMemCh:
		result.MemoryUsed = mem
	case <-time.After(100 * time.Millisecond):
		result.MemoryUsed = 0
	}

	// 5. Логи
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

	return result, nil
}