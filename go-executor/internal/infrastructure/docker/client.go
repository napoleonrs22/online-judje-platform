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

	// 5. Запускаем компиляцию в Docker (файлы в /app через CopyToContainer, без bind)
	log.Printf("🔨 Compiling %s (file: %s)...", language, fileName)

	var after func(context.Context, string) error
	if language == "java" {
		after = func(c context.Context, cid string) error {
			return d.copyJavaClasses(c, cid, workDir)
		}
	} else {
		bin := cfg.BinName
		after = func(c context.Context, cid string) error {
			return d.copyPathFromContainer(c, cid, "/app/"+bin, filepath.Join(workDir, bin))
		}
	}

	resp, err := d.runContainer(ctx, cfg.Image, cfg.CompileCmd, "", workDir, nil, 3000, 1024, nil, after)
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

	// Файлы в /app через CopyToContainer; ввод в stdin через Attach.
	res, err := d.runContainer(ctx, cfg.Image, cfg.RunCmd, "", workDir, nil, timeLimit, memLimit, []byte(inputData), nil)

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

	actualOut := strings.TrimSpace(res.Stdout)
	if res.ExitCode != 0 {
		if se := strings.TrimSpace(res.Stderr); se != "" {
			if actualOut != "" {
				actualOut = se + "\n" + actualOut
			} else {
				actualOut = se
			}
		}
	}

	return domain.TestResult{
		Status:          status,
		ActualOutput:    actualOut,
		ExecutionTimeMs: int(res.Duration.Milliseconds()),
		MemoryUsedMB:    int(res.MemoryUsed / 1024 / 1024),
	}, nil
}

func (d *DockerExecutor) Cleanup(workDir string) {
	os.RemoveAll(workDir)
}

func (d *DockerExecutor) copyPathFromContainer(ctx context.Context, containerID, srcPath, destHostPath string) error {
	r, _, err := d.cli.CopyFromContainer(ctx, containerID, srcPath)
	if err != nil {
		return err
	}
	defer r.Close()
	return copyFileFromContainerTar(r, destHostPath)
}

func (d *DockerExecutor) copyJavaClasses(ctx context.Context, containerID, destDir string) error {
	r, _, err := d.cli.CopyFromContainer(ctx, containerID, "/app")
	if err != nil {
		return err
	}
	defer r.Close()
	return extractClassFilesFromTar(r, destDir)
}