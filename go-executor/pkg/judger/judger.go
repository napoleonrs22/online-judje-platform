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
	"regexp"
	"strings"
	"time"

	"go-executor/pkg/models"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
)

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
		return "gcc:latest", "sh -c \"g++ -o solution user_code.cpp -O2 -static && ./solution < input.txt\"", nil
	case "java":
		return "eclipse-temurin:17-jdk-alpine", "sh -c \"javac Solution.java && java Solution < input.txt\"", nil
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

// Исправляем Java класс
func fixJavaClassName(code string) string {
	re := regexp.MustCompile(`(?i)(public\s+class\s+)(\w+)(\s+\{)`)
	fixed := re.ReplaceAllString(code, "${1}Solution${3}")
	return fixed
}

func sanitizeOutput(output string) string {
	return strings.TrimSpace(output)
}

func (j *dockerJudger) getContainerOutput(ctx context.Context, containerID string) (stdout, stderr string, err error) {
	log.Printf("📋 [DEBUG] Получаем логи контейнера: %s", containerID[:12])

	logs, err := j.cli.ContainerLogs(ctx, containerID, container.LogsOptions{
		ShowStdout: true,
		ShowStderr: true,
		Follow:     false,
		Timestamps: false,
	})
	if err != nil {
		log.Printf("❌ [DEBUG] Ошибка получения логов: %v", err)
		return "", "", fmt.Errorf("ошибка получения логов: %w", err)
	}
	defer logs.Close()

	var outBuf, errBuf bytes.Buffer
	_, err = stdcopy.StdCopy(&outBuf, &errBuf, logs)
	if err != nil && err != io.EOF {
		log.Printf("❌ [DEBUG] Ошибка чтения логов: %v", err)
		return "", "", fmt.Errorf("ошибка чтения логов: %w", err)
	}

	log.Printf("✅ [DEBUG] Логи получены: stdout=%d bytes, stderr=%d bytes", len(outBuf.String()), len(errBuf.String()))
	return outBuf.String(), errBuf.String(), nil
}

func (j *dockerJudger) getMemoryUsage(ctx context.Context, containerID string) (int, error) {
	log.Printf("📊 [DEBUG] Получаем использование памяти: %s", containerID[:12])

	stats, err := j.cli.ContainerStats(ctx, containerID, false)
	if err != nil {
		log.Printf("❌ [DEBUG] Ошибка получения статистики: %v", err)
		return 0, err
	}
	defer stats.Body.Close()

	var v container.StatsResponse
	if err := json.NewDecoder(stats.Body).Decode(&v); err != nil {
		log.Printf("❌ [DEBUG] Ошибка декодирования статистики: %v", err)
		return 0, err
	}

	memoryMB := int(v.MemoryStats.Usage / 1024 / 1024)
	log.Printf("✅ [DEBUG] Память: %d MB", memoryMB)
	return memoryMB, nil
}

func (j *dockerJudger) copyFileToContainer(ctx context.Context, containerID, srcPath, dstPath string) error {
	log.Printf("📁 [DEBUG] Копирование файла: %s → %s", filepath.Base(srcPath), dstPath)

	content, err := os.ReadFile(srcPath)
	if err != nil {
		log.Printf("❌ [DEBUG] Ошибка чтения файла: %v", err)
		return fmt.Errorf("ошибка чтения файла %s: %w", srcPath, err)
	}

	log.Printf("   Размер файла: %d bytes", len(content))

	var buf bytes.Buffer
	tw := tar.NewWriter(&buf)

	fileName := filepath.Base(dstPath)

	hdr := &tar.Header{
		Name: fileName,
		Mode: 0644,
		Size: int64(len(content)),
	}
	if err := tw.WriteHeader(hdr); err != nil {
		log.Printf("❌ [DEBUG] Ошибка записи tar header: %v", err)
		return fmt.Errorf("ошибка записи заголовка tar: %w", err)
	}

	if _, err := tw.Write(content); err != nil {
		log.Printf("❌ [DEBUG] Ошибка записи содержимого: %v", err)
		return fmt.Errorf("ошибка записи содержимого файла: %w", err)
	}

	if err := tw.Close(); err != nil {
		log.Printf("❌ [DEBUG] Ошибка закрытия tar: %v", err)
		return fmt.Errorf("ошибка закрытия tar writer: %w", err)
	}

	dir := filepath.Dir(dstPath)
	err = j.cli.CopyToContainer(ctx, containerID, dir, &buf, container.CopyToContainerOptions{})
	if err != nil {
		log.Printf("❌ [DEBUG] Ошибка копирования в контейнер: %v", err)
		return fmt.Errorf("ошибка копирования в контейнер: %w", err)
	}

	log.Printf("✅ [DEBUG] Файл успешно скопирован")
	return nil
}

// executeInContainer - Основная функция запуска Docker-контейнера
func (j *dockerJudger) executeInContainer(ctx context.Context, req models.JudgerRequest, codePath string, inputPath string) (output string, runTime int, memoryUsed int, runError string, status string, err error) {
	log.Printf("\n" + strings.Repeat("=", 60))
	log.Printf("🚀 [EXECUTE] Начинаем выполнение кода")
	log.Printf("   Язык: %s | Timeout: %dms | Memory: %dmb", req.Language, req.TimeLimit, req.MemoryLimit)
	log.Printf(strings.Repeat("=", 60))

	image, command, err := getLanguageConfig(req.Language)
	if err != nil {
		log.Printf("❌ [ERROR] Неподдерживаемый язык: %v", err)
		return "", 0, 0, "", models.StatusInternalError, err
	}
	codeFileName := getCodeFileName(req.Language)
	log.Printf("📦 [DEBUG] Образ: %s | Команда: %s", image, command)

	// Увеличиваем минимум памяти для Python
	memoryLimit := req.MemoryLimit
	if memoryLimit < 512 {
		memoryLimit = 512 // минимум 512 MB
		log.Printf("⚠️  [DEBUG] Память слишком мала, используем минимум 512 MB")
	}

	pidsLimit := int64(100)

	hostConfig := &container.HostConfig{
		Resources: container.Resources{
			Memory:   int64(memoryLimit) * 1024 * 1024,
			NanoCPUs: 1000000000,
			PidsLimit: &pidsLimit,
			OomKillDisable: func(b bool) *bool { return &b }(false),
		},
		NetworkMode:    "none",
		ReadonlyRootfs: false,
		SecurityOpt:    []string{"no-new-privileges"},
	}

	config := &container.Config{
		Image:      image,
		Cmd:        []string{"sh", "-c", command},
		WorkingDir: "/usr/app",
		Tty:        false,
	}

	log.Printf("🔨 [DEBUG] Создаём контейнер...")
	resp, err := j.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, "")
	if err != nil {
		log.Printf("❌ [ERROR] Ошибка создания контейнера: %v", err)
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка создания контейнера: %w", err)
	}
	containerID := resp.ID
	log.Printf("✅ [DEBUG] Контейнер создан: %s", containerID[:12])

	defer func() {
		log.Printf("🗑️  [DEBUG] Удаляем контейнер: %s", containerID[:12])
		j.cli.ContainerRemove(context.Background(), containerID, container.RemoveOptions{Force: true, RemoveVolumes: true})
	}()

	// Копируем файлы в контейнер
	log.Printf("📂 [DEBUG] Копируем файлы...")
	if err := j.copyFileToContainer(ctx, containerID, codePath, "/usr/app/"+codeFileName); err != nil {
		log.Printf("❌ [ERROR] Ошибка копирования кода: %v", err)
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка копирования кода: %w", err)
	}
	if err := j.copyFileToContainer(ctx, containerID, inputPath, "/usr/app/input.txt"); err != nil {
		log.Printf("❌ [ERROR] Ошибка копирования входных данных: %v", err)
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка копирования входных данных: %w", err)
	}
	log.Printf("✅ [DEBUG] Все файлы скопированы")

	log.Printf("▶️  [DEBUG] Запускаем контейнер...")
	startTime := time.Now()
	if err := j.cli.ContainerStart(ctx, containerID, container.StartOptions{}); err != nil {
		log.Printf("❌ [ERROR] Ошибка запуска контейнера: %v", err)
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка запуска контейнера: %w", err)
	}
	log.Printf("✅ [DEBUG] Контейнер запущен")

	log.Printf("⏳ [DEBUG] Ожидаем завершения (timeout: %dms)...", req.TimeLimit)

	// ← ИСПРАВЛЕНИЕ: Для C++/Java увеличиваем timeout (компиляция требует времени)
	timeout := req.TimeLimit
	if req.Language == "cpp" || req.Language == "java" {
		timeout = req.TimeLimit * 3  // В 2 раза больше для компиляции
		log.Printf("⏰ [DEBUG] C++/Java - увеличенный timeout: %dms", timeout)
	}

	waitTimeout := time.Duration(timeout) * time.Millisecond
	ctxWait, cancelWait := context.WithTimeout(ctx, waitTimeout)
	defer cancelWait()

	waitCh, errCh := j.cli.ContainerWait(ctxWait, containerID, container.WaitConditionNotRunning)

	var exitCode int64 = -1
	select {
	case <-ctxWait.Done():
		log.Printf("⏱️  [TIMEOUT] Время истекло! Убиваем контейнер...")
		_ = j.cli.ContainerKill(context.Background(), containerID, "SIGKILL")
		// ← ИСПРАВЛЕНИЕ: Получаем память перед возвратом
		memUsed, _ := j.getMemoryUsage(context.Background(), containerID)
		return "", timeout, memUsed, "Time Limit Exceeded", models.StatusTimeLimit, nil
	case err := <-errCh:
		log.Printf("❌ [ERROR] Ошибка ожидания контейнера: %v", err)
		return "", 0, 0, "", models.StatusInternalError, fmt.Errorf("ошибка ожидания контейнера: %w", err)
	case result := <-waitCh:
		exitCode = result.StatusCode
		log.Printf("✅ [DEBUG] Контейнер завершился с exit code: %d", exitCode)
	}

	runTime = int(time.Since(startTime).Milliseconds())
	log.Printf("📊 [DEBUG] Время выполнения: %dms", runTime)

	// ← ИСПРАВЛЕНИЕ: Получаем память ДО удаления контейнера
	memoryUsed, memErr := j.getMemoryUsage(context.Background(), containerID)
	if memErr != nil {
		log.Printf("⚠️  [DEBUG] Ошибка получения памяти: %v", memErr)
		memoryUsed = 0
	}

	log.Printf("📋 [DEBUG] Получаем вывод...")
	stdout, stderr, _ := j.getContainerOutput(context.Background(), containerID)

	log.Printf("📤 [DEBUG] STDOUT (%d bytes):\n%s", len(stdout), stdout)
	log.Printf("📤 [DEBUG] STDERR (%d bytes):\n%s", len(stderr), stderr)

	output = stdout

	if exitCode != 0 {
		status := models.StatusRuntimeError
		runError = stderr

		if (req.Language == "cpp" || req.Language == "java") && len(stdout) == 0 && len(stderr) > 0 {
			status = models.StatusCompileError
			log.Printf("🔴 [COMPILE_ERROR] Ошибка компиляции для %s", req.Language)
		} else {
			log.Printf("🔴 [RUNTIME_ERROR] Exit code: %d", exitCode)
		}

		return output, runTime, memoryUsed, runError, status, nil
	}

	log.Printf("🟢 [SUCCESS] Контейнер успешно завершился")
	return output, runTime, memoryUsed, "", models.StatusAccepted, nil
}

// Execute - Общая логика Judger
func (j *dockerJudger) Execute(ctx context.Context, req models.JudgerRequest) (models.JudgerResponse, error) {
	log.Printf("\n" + strings.Repeat("=", 60))
	log.Printf("📨 [NEW_REQUEST] Язык: %s | Код длина: %d | Входные данные: %d bytes", req.Language, len(req.Code), len(req.InputData))
	log.Printf(strings.Repeat("=", 60))

	tempDir, err := os.MkdirTemp(sharedDir, "judge_sandbox_*")
	if err != nil {
		log.Printf("❌ [ERROR] Ошибка создания временной директории: %v", err)
		return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось создать временную директорию."}, nil
	}
	log.Printf("📁 [DEBUG] Временная директория: %s", tempDir)
	defer os.RemoveAll(tempDir)

	codeFileName := getCodeFileName(req.Language)
	codeFile := filepath.Join(tempDir, codeFileName)
	inputFile := filepath.Join(tempDir, "input.txt")

	// Исправляем Java класс перед сохранением
	code := req.Code
	if req.Language == "java" {
		log.Printf("🔧 [DEBUG] Исправляем Java класс...")
		code = fixJavaClassName(code)
		log.Printf("   Класс переименован в Solution")
	}

	log.Printf("💾 [DEBUG] Сохраняем файлы...")
	if err := os.WriteFile(codeFile, []byte(code), 0644); err != nil {
		log.Printf("❌ [ERROR] Ошибка записи кода: %v", err)
		return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось записать код."}, nil
	}
	if err := os.WriteFile(inputFile, []byte(req.InputData), 0644); err != nil {
		log.Printf("❌ [ERROR] Ошибка записи входных данных: %v", err)
		return models.JudgerResponse{Status: models.StatusInternalError, Details: "Не удалось записать входные данные."}, nil
	}
	log.Printf("✅ [DEBUG] Файлы сохранены")

	actualOutput, runTime, memoryUsed, runError, status, err := j.executeInContainer(ctx, req, codeFile, inputFile)

	if err != nil {
		log.Printf("❌ [ERROR] Ошибка исполнения контейнера: %v", err)
		return models.JudgerResponse{Status: models.StatusInternalError, Details: err.Error()}, nil
	}

	if status != models.StatusAccepted {
		log.Printf("🔴 [RESULT] Статус: %s", status)
		return models.JudgerResponse{
			Status:          status,
			ActualOutput:    actualOutput,
			ExecutionTimeMs: runTime,
			MemoryUsedMB:    memoryUsed,
			Details:         runError,
		}, nil
	}

	// Сравнение вывода (Финальный Чекер)
	expected := sanitizeOutput(req.ExpectedOutput)
	actual := sanitizeOutput(actualOutput)

	log.Printf("🔍 [CHECKER] Сравнение вывода:")
	log.Printf("   Ожидается: '%s'", expected)
	log.Printf("   Получено: '%s'", actual)

	if req.CheckerType == "exact" {
		if actual == expected {
			log.Printf("🟢 [FINAL] ACCEPTED ✅")
			return models.JudgerResponse{
				Status:          models.StatusAccepted,
				ActualOutput:    actual,
				ExecutionTimeMs: runTime,
				MemoryUsedMB:    memoryUsed,
				Details:         "OK",
			}, nil
		}

		log.Printf("🔴 [FINAL] WRONG_ANSWER ❌")
		return models.JudgerResponse{
			Status:          models.StatusWrongAnswer,
			ActualOutput:    actual,
			ExecutionTimeMs: runTime,
			MemoryUsedMB:    memoryUsed,
			Details:         fmt.Sprintf("Output mismatch. Expected: '%s', Got: '%s'", expected, actual),
		}, nil
	}

	log.Printf("🔴 [FINAL] INTERNAL_ERROR - Checker type not implemented")
	return models.JudgerResponse{
		Status:          models.StatusInternalError,
		ActualOutput:    actual,
		ExecutionTimeMs: runTime,
		MemoryUsedMB:    memoryUsed,
		Details:         "Checker type not implemented.",
	}, nil
}