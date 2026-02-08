package usecase

import (
	"context"
	"go-executor/internal/domain"
	"log"
	"os"
	"strings"
)

type JudgeService struct {
	compiler domain.Compiler
	runner   domain.Runner
}

func NewJudgeService(compiler domain.Compiler, runner domain.Runner) *JudgeService {
	return &JudgeService{compiler: compiler, runner: runner}
}

func (s *JudgeService) Execute(ctx context.Context, req domain.ExecutionRequest) domain.ExecutionResponse {
	// Инициализируем ответ по умолчанию
	resp := domain.ExecutionResponse{
		SubmissionID: req.SubmissionID,
		FinalStatus:  "ACCEPTED",
		TestResults:  make([]domain.TestResult, 0),
	}

	// 1. Подготовка рабочей директории
	// Читаем путь к общей папке из переменной окружения (задана в docker-compose)
	baseDir := os.Getenv("JUDGER_SHARED_DIR")
	if baseDir == "" {
		// Если переменная не задана, используем системный tmp (но это может вызвать ошибку mounts denied)
		baseDir = os.TempDir()
		log.Println("⚠️  Warning: JUDGER_SHARED_DIR not set, using default temp dir")
	}

	// Создаем уникальную папку для этого решения
	workDir, err := os.MkdirTemp(baseDir, "sandbox_"+req.SubmissionID+"_")
	if err != nil {
		log.Printf("❌ Failed to create work dir: %v", err)
		resp.FinalStatus = "INTERNAL_ERROR"
		resp.ErrorMessage = "Failed to create sandbox environment: " + err.Error()
		return resp
	}

	// ВАЖНО: Удаляем папку после завершения функции (независимо от успеха или ошибки)
	defer s.runner.Cleanup(workDir)

	log.Printf("📂 Created sandbox: %s", workDir)

	// 2. Компиляция кода
	binPath, err := s.compiler.Compile(ctx, req.Code, req.Language, workDir)
	if err != nil {
		log.Printf("❌ Compilation failed: %v", err)
		resp.FinalStatus = "COMPILE_ERROR"
		resp.ErrorMessage = err.Error()
		return resp
	}

	// 3. Запуск тестов
	var maxTime int
	var maxMem int

	for _, tc := range req.TestCases {
		// Запуск одного теста
		runRes, err := s.runner.Run(ctx, binPath, req.Language, workDir, tc.InputData, req.TimeLimit, req.MemoryLimit)

		if err != nil {
			log.Printf("❌ Runner error on test %s: %v", tc.ID, err)
			runRes.Status = "INTERNAL_ERROR"
			runRes.ActualOutput = "System Error: " + err.Error()
		}

		// Логика проверки (Checker)
		if runRes.Status == "ACCEPTED" {
			expected := strings.TrimSpace(tc.ExpectedOutput)
			actual := strings.TrimSpace(runRes.ActualOutput)

			if expected != actual {
				runRes.Status = "WRONG_ANSWER"
			}
		}

		// Сборка результата для отправки обратно в Python
		resultModel := domain.TestResult{
			ID:              tc.ID,
			Status:          runRes.Status,
			ActualOutput:    runRes.ActualOutput,
			ExecutionTimeMs: runRes.ExecutionTimeMs,
			MemoryUsedMB:    runRes.MemoryUsedMB,

			// --- ОБЯЗАТЕЛЬНЫЕ ПОЛЯ ДЛЯ FastAPI ---
			IsPassed: runRes.Status == "ACCEPTED",
			Details:  runRes.ActualOutput, // Можно расширить (например, добавить ожидаемый вывод при ошибке)
		}

		resp.TestResults = append(resp.TestResults, resultModel)

		// Считаем макс. ресурсы
		if resultModel.ExecutionTimeMs > maxTime {
			maxTime = resultModel.ExecutionTimeMs
		}
		if resultModel.MemoryUsedMB > maxMem {
			maxMem = resultModel.MemoryUsedMB
		}

		// Обновляем глобальный статус (если хоть один тест упал — решение не принято)
		if resultModel.Status != "ACCEPTED" && resp.FinalStatus == "ACCEPTED" {
			resp.FinalStatus = resultModel.Status
			if resultModel.Status == "RUNTIME_ERROR" || resultModel.Status == "COMPILE_ERROR" {
				resp.ErrorMessage = resultModel.ActualOutput
			}
		}
	}

	resp.MaxTimeMs = maxTime
	resp.MaxMemoryMB = maxMem

	log.Printf("🏁 Execution finished. Status: %s, Time: %dms, Mem: %dMB", resp.FinalStatus, maxTime, maxMem)
	return resp
}