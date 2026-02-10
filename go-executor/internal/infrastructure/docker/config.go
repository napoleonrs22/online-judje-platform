package docker

import (
	"fmt"
)

type LangConfig struct {
	Image      string
	CompileCmd []string
	RunCmd     []string
	IsCompiled bool
	SourceExt  string
	BinName    string
}

// getLangConfig возвращает конфигурацию для языка
func getLangConfig(language, workDir, fileName string) (LangConfig, error) {
	switch language {
	case "python":
		return LangConfig{
			Image:      "python:3.10-slim",
			IsCompiled: false,
			SourceExt:  "py",
			RunCmd:     []string{"python3", "-u", fileName},
		}, nil

	case "cpp":
		return LangConfig{
			Image:      "gcc:latest",
			IsCompiled: true,
			SourceExt:  "cpp",
			BinName:    "solution",
			CompileCmd: []string{"g++", "-O2", "-o", "solution", fileName, "-static"},
			RunCmd:     []string{"./solution"},
		}, nil

	case "java":
		return LangConfig{
			Image:      "eclipse-temurin:17-jdk-alpine",
			IsCompiled: true,
			SourceExt:  "java",
			BinName:    "Solution",
			CompileCmd: []string{"javac", fileName},
			RunCmd:     []string{"java", "Solution"},
		}, nil

	case "go":
		return LangConfig{
			Image:      "golang:1.23-alpine",
			IsCompiled: true,
			SourceExt:  "go",
			BinName:    "main",
			CompileCmd: []string{"go", "build", "-o", "main", fileName},
			RunCmd:     []string{"./main"},
		}, nil

	case "javascript":
		return LangConfig{
			Image:      "node:18-alpine",
			IsCompiled: false,
			SourceExt:  "js",
			RunCmd:     []string{"node", fileName},
		}, nil

	default:
		return LangConfig{}, fmt.Errorf("unsupported language: %s", language)
	}
}