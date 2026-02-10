package docker

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"go-executor/internal/domain"

	"github.com/docker/docker/client"
)

type DockerExecutor struct {
	cli *client.Client
}

func NewDockerExecutor() (*DockerExecutor, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return nil, err
	}
	return &DockerExecutor{cli: cli}, nil
}

// --- Compiler Implementation ---

func (d *DockerExecutor) Compile(ctx context.Context, code, language, workDir string) (string, error) {
	// 1. Исправляем имя Java-класса на Solution (если нужно)
	if language == "java" {
		re := regexp.MustCompile(`(?i)(public\s+class\s+)(\w+)(\s*\{)`)
		code = re.ReplaceAllString(code, "${1}Solution${3}")
	}

	// 2. Сначала получаем "черновой" конфиг, чтобы узнать расширение файла
	preCfg, err := getLangConfig(language, workDir, "dummy")
	if err != nil {
		return "", err
	}

	// Определяем правильное имя файла
	fileName := "solution." + preCfg.SourceExt
	if language == "java" {
		fileName = "Solution.java"
	}

	// 3. Получаем "чистовой" конфиг с правильным именем файла
	// Это ВАЖНО, чтобы CompileCmd был "javac Solution.java", а не "javac dummy"
	cfg, err := getLangConfig(language, workDir, fileName)
	if err != nil {
		return "", err
	}

	// 4. Сохраняем код на диск
	srcPath := filepath.Join(workDir, fileName)
	if err := os.WriteFile(srcPath, []byte(code), 0777); err != nil {
		return "", fmt.Errorf("failed to save code: %w", err)
	}

	// Если язык интерпретируемый, возвращаем имя файла (компиляция не нужна)
	if !cfg.IsCompiled {
		return fileName, nil
	}

	// 5. Запускаем компиляцию в Docker
	log.Printf("🔨 Compiling %s (file: %s)...", language, fileName)

	resp, err := d.runContainer(ctx, cfg.Image, cfg.CompileCmd, workDir, nil, 3000, 1024)
	if err != nil {
		return "", err
	}

	if resp.ExitCode != 0 {
		return "", fmt.Errorf("Compilation Error:\n%s", resp.Stderr)
	}

	return cfg.BinName, nil
}

// --- Runner Implementation ---

func (d *DockerExecutor) Run(ctx context.Context, binPath, language, workDir, inputData string, timeLimit, memLimit int) (domain.TestResult, error) {
	// Получаем конфиг запуска
	cfg, err := getLangConfig(language, workDir, binPath)
	if err != nil {
		return domain.TestResult{Status: "INTERNAL_ERROR"}, err
	}

	// Создаем файл с входными данными
	inputFile := "input.txt"
	if err := os.WriteFile(filepath.Join(workDir, inputFile), []byte(inputData), 0777); err != nil {
		return domain.TestResult{Status: "INTERNAL_ERROR"}, err
	}

	// Формируем команду запуска: command < input.txt
	fullCmd := []string{"sh", "-c", fmt.Sprintf("%s < %s", strings.Join(cfg.RunCmd, " "), inputFile)}

	// Запускаем контейнер
	res, err := d.runContainer(ctx, cfg.Image, fullCmd, workDir, nil, timeLimit, memLimit)

	if err != nil {
		return domain.TestResult{Status: "INTERNAL_ERROR", ActualOutput: err.Error()}, nil
	}

	// Формируем вердикт
	status := "ACCEPTED"
	if res.OOMKilled {
		status = "MEMORY_LIMIT"
	} else if res.Timeout {
		status = "TIME_LIMIT"
	} else if res.ExitCode != 0 {
		status = "RUNTIME_ERROR"
	}

	return domain.TestResult{
		Status:          status,
		ActualOutput:    strings.TrimSpace(res.Stdout),
		ExecutionTimeMs: int(res.Duration.Milliseconds()),
		MemoryUsedMB:    int(res.MemoryUsed / 1024 / 1024),
	}, nil
}

func (d *DockerExecutor) Cleanup(workDir string) {
	os.RemoveAll(workDir)
}