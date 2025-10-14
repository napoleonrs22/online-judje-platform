
// go-executor/pkg/judger/judger.go

package judger

import (
    "archive/tar"
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "os"
    "path/filepath"
    "strings"
    "time"

    "go-executor/pkg/models"
    
    "github.com/docker/docker/api/types/container"
    "github.com/docker/docker/client"
    "github.com/docker/docker/pkg/stdcopy"
)



const EXECUTION_IMAGE = "python:3.10-slim" 


var sharedDir = os.Getenv("JUDGER_SHARED_DIR") 

func init() {
	if sharedDir == "" {
		sharedDir = os.TempDir() 
	}
}

type Judger interface {
	Execute(ctx context.Context, req models.JudgerRequest) (models.JudgerResponse, error) 
}

type dockerJudger struct {
	cli *client.Client
}

func NewDockerJudger() (Judger, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return nil, fmt.Errorf("ошибка инициализации клиента Docker: %w", err)
	}
	log.Println("✅ Judger: Docker-клиент успешно инициализирован.")
	return &dockerJudger{cli: cli}, nil
}

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

func getLanguageConfig(language string) (string, string, error) {
	switch language {
	case "python":
		return "python:3.10-slim", "python user_code.py < input.txt", nil 
	case "cpp":
		return "gcc:latest", "sh -c \"g++ -o solution user_code.cpp && ./solution < input.txt\"", nil
	case "java":
		return "openjdk:17-alpine", "sh -c \"javac Solution.java && timeout 1 java Solution < input.txt\"", nil
	case "javascript":
		return "node:18-alpine", "node user_code.js < input.txt", nil
	default:
		return "", "", fmt.Errorf("неподдерживаемый язык: %s", language)
	}
}

func getCodeFileName(language string) string {
	switch language {
	case "python":
		return "user_code.py"
	case "cpp":
		return "user_code.cpp"
	case "java":
		return "Solution.java"
	case "javascript":
		return "user_code.js"
	default:
		return "user_code.txt"
	}
}

func sanitizeOutput(output string) string {
	return strings.TrimSpace(output)
}

func (j *dockerJudger) getContainerOutput(ctx context.Context, containerID string) (stdout, stderr string, err error) {
	logs, err := j.cli.ContainerLogs(ctx, containerID, container.LogsOptions{
		ShowStdout: true,
		ShowStderr: true,
		Follow:     false,
		Timestamps: false,
	})
	if err != nil {
		return "", "", fmt.Errorf("ошибка получения логов: %w", err)
	}
	defer logs.Close()

	var outBuf, errBuf bytes.Buffer
	_, err = stdcopy.StdCopy(&outBuf, &errBuf, logs)
	if err != nil && err != io.EOF {
		return "", "", fmt.Errorf("ошибка чтения логов: %w", err)
	}

	return outBuf.String(), errBuf.String(), nil
}

func (j *dockerJudger) getMemoryUsage(ctx context.Context, containerID string) (int, error) {
	stats, err := j.cli.ContainerStats(ctx, containerID, false)
	if err != nil {
		return 0, err
	}
	defer stats.Body.Close()

	var v container.StatsResponse
	if err := json.NewDecoder(stats.Body).Decode(&v); err != nil {
		return 0, err
	}

	memoryMB := int(v.MemoryStats.Usage / 1024 / 1024)
	return memoryMB, nil
}

func (j *dockerJudger) copyFileToContainer(ctx context.Context, containerID, srcPath, dstPath string) error {
	// Читаем содержимое файла
	content, err := os.ReadFile(srcPath)
	if err != nil {
		return fmt.Errorf("ошибка чтения файла %s: %w", srcPath, err)
	}

	// Создаем tar архив с файлом
	var buf bytes.Buffer
	tw := tar.NewWriter(&buf)
	
	// Получаем имя файла из пути
	fileName := filepath.Base(dstPath)
	
	// Записываем заголовок файла
	hdr := &tar.Header{
		Name: fileName,
		Mode: 0644,
		Size: int64(len(content)),
	}
	if err := tw.WriteHeader(hdr); err != nil {
		return fmt.Errorf("ошибка записи заголовка tar: %w", err)
	}
	
	// Записываем содержимое файла
	if _, err := tw.Write(content); err != nil {
		return fmt.Errorf("ошибка записи содержимого файла: %w", err)
	}
	
	if err := tw.Close(); err != nil {
		return fmt.Errorf("ошибка закрытия tar writer: %w", err)
	}

	// Копируем tar архив в контейнер
	dir := filepath.Dir(dstPath)
	err = j.cli.CopyToContainer(ctx, containerID, dir, &buf, container.CopyToContainerOptions{})
	if err != nil {
		return fmt.Errorf("ошибка копирования в контейнер: %w", err)
	}

	return nil
}


// executeInContainer - Основная функция запуска Docker-контейнера
func (j *dockerJudger) executeInContainer(ctx context.Context, req models.JudgerRequest, codePath string, inputPath string) (output string, runTime int, memoryUsed int, runError string, status string, err error) {
	
	image, command, err := getLanguageConfig(req.Language)
	if err != nil {
		return "", 0, 0, "", models.StatusInternalError, err
	}
	codeFileName := getCodeFileName(req.Language)
	
	pidsLimit := int64(100)
	
	hostConfig := &container.HostConfig{
		Resources: container.Resources{
			Memory:   int64(req.MemoryLimit) * 1024 * 1024,
			NanoCPUs: 1000000000, 
			PidsLimit: &pidsLimit, // ИСПРАВЛЕНА ОШИБКА ТИПА
			OomKillDisable: func(b bool) *bool { return &b }(false),
		},
		NetworkMode: "none", 
		ReadonlyRootfs: false, 
		SecurityOpt: []string{"no-new-privileges"},
	}
	
	config := &container.Config{
		Image:      image,
		Cmd:        []string{"sh", "-c", command}, 
		WorkingDir: "/usr/app", 
		Tty:        false,
	}

	resp, err := j.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, "")
	if err != nil {
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка создания контейнера: %w", err)
	}
	containerID := resp.ID

	defer func() {
		j.cli.ContainerRemove(context.Background(), containerID, container.RemoveOptions{Force: true, RemoveVolumes: true})
	}()

	// Копируем файлы в контейнер
	if err := j.copyFileToContainer(ctx, containerID, codePath, "/usr/app/"+codeFileName); err != nil {
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка копирования кода: %w", err)
	}
	if err := j.copyFileToContainer(ctx, containerID, inputPath, "/usr/app/input.txt"); err != nil {
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка копирования входных данных: %w", err)
	}

	startTime := time.Now()
	if err := j.cli.ContainerStart(ctx, containerID, container.StartOptions{}); err != nil {
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка запуска контейнера: %w", err)
	}

	waitTimeout := time.Duration(req.TimeLimit) * time.Millisecond
	ctxWait, cancelWait := context.WithTimeout(ctx, waitTimeout)
	defer cancelWait()
	
	waitCh, errCh := j.cli.ContainerWait(ctxWait, containerID, container.WaitConditionNotRunning)

	var exitCode int64 = -1
	select {
	case <-ctxWait.Done():
		_ = j.cli.ContainerKill(context.Background(), containerID, "SIGKILL")
		return "", req.TimeLimit, 0, "Time Limit Exceeded", models.StatusTimeLimit, nil
	case err := <-errCh:
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка ожидания контейнера: %w", err)
	case result := <-waitCh:
		exitCode = result.StatusCode
	}
	
	runTime = int(time.Since(startTime).Milliseconds()) 
	memoryUsed, _ = j.getMemoryUsage(context.Background(), containerID)

	stdout, stderr, _ := j.getContainerOutput(context.Background(), containerID)

	output = stdout 

	if exitCode != 0 {
		status := models.StatusRuntimeError
		runError = stderr
		
		if (req.Language == "cpp" || req.Language == "java") && len(stdout) == 0 && len(stderr) > 0 {
			status = models.StatusCompileError
		}
		
		return output, runTime, memoryUsed, runError, status, nil
	}
	
	return output, runTime, memoryUsed, "", models.StatusAccepted, nil
}


// Execute - Общая логика Judger
func (j *dockerJudger) Execute(ctx context.Context, req models.JudgerRequest) (models.JudgerResponse, error) { // ИСПРАВЛЕНО
	
	tempDir, err := os.MkdirTemp(sharedDir, "judge_sandbox_*") // ИСПОЛЬЗУЕМ sharedDir!
    if err != nil {
        return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось создать временную директорию."}, nil
    }
    defer os.RemoveAll(tempDir) 
	
	codeFile := filepath.Join(tempDir, getCodeFileName(req.Language))
	inputFile := filepath.Join(tempDir, "input.txt")
	
	if err := os.WriteFile(codeFile, []byte(req.Code), 0644); err != nil {
		return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось записать код."}, nil
	}
	if err := os.WriteFile(inputFile, []byte(req.InputData), 0644); err != nil {
		return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось записать входные данные."}, nil
	}

	actualOutput, runTime, memoryUsed, runError, status, err := j.executeInContainer(ctx, req, codeFile, inputFile)

	if err != nil {
		log.Printf("Judger: Ошибка исполнения контейнера: %v", err)
		return models.JudgerResponse{Status: models.StatusInternalError, Details: err.Error()}, nil
	}

	if status != models.StatusAccepted {
		return models.JudgerResponse{
			Status: status,
			ActualOutput: actualOutput,
			ExecutionTimeMs: runTime,
			MemoryUsedMB: memoryUsed,
			Details: runError,
		}, nil
	}
	
	// 5. Сравнение вывода (Финальный Чекер)
	expected := sanitizeOutput(req.ExpectedOutput)
	actual := sanitizeOutput(actualOutput)

	if req.CheckerType == "exact" { 
		if actual == expected {
			return models.JudgerResponse{
				Status: models.StatusAccepted,
				ActualOutput: actual,
				ExecutionTimeMs: runTime,
				MemoryUsedMB: memoryUsed,
				Details: "OK",
			}, nil
		}
		
		return models.JudgerResponse{
			Status: models.StatusWrongAnswer,
			ActualOutput: actual,
			ExecutionTimeMs: runTime,
			MemoryUsedMB: memoryUsed,
			Details: fmt.Sprintf("Output mismatch. Expected: '%s', Got: '%s'", expected, actual),
		}, nil
	}

	return models.JudgerResponse{
		Status: models.StatusInternalError,
		ActualOutput: actual,
		ExecutionTimeMs: runTime,
		MemoryUsedMB: memoryUsed,
		Details: "Checker type not implemented.",
	}, nil
}