package service

import (
	"context"
	"go-executor/pkg/judger"
	"go-executor/pkg/models"
	"log"
)

// SubmissionService - Интерфейс для сервиса проверки
type SubmissionService interface {
	JudgeSubmission(ctx context.Context, req models.ExecutionRequest) (models.ExecutionResponse, error)
}

// submissionService - Реализация
type submissionService struct {
	judger judger.Judger
}

func NewSubmissionService(j judger.Judger) SubmissionService {
	return &submissionService{judger: j}
}

// JudgeSubmission - Главная логика проверки (агрегация результатов Judger)
func (s *submissionService) JudgeSubmission(ctx context.Context, req models.ExecutionRequest) (models.ExecutionResponse, error) {
	
	finalResponse := models.ExecutionResponse{
		SubmissionID: req.SubmissionID,
		TestResults: make([]models.TestResult, 0, len(req.TestCases)),
	}

	maxTime := 0
	maxMemory := 0
	finalStatus := models.StatusAccepted 

	for i, tc := range req.TestCases {
		
		// 1. Формирование запроса для Judger
		// FIX: Используем models.JudgerRequest
		judgerReq := models.JudgerRequest{ 
			Language: req.Language,
			Code: req.Code,
			TimeLimit: req.TimeLimit,
			MemoryLimit: req.MemoryLimit,
			CheckerType: req.CheckerType,
			InputData: tc.InputData,
			ExpectedOutput: tc.ExpectedOutput,
		}
		
		// 2. Вызов Judger (Песочницы)
		// Judger.Execute ожидает models.JudgerRequest
		judgerResult, err := s.judger.Execute(ctx, judgerReq) 
		
		if err != nil {
			log.Printf("Service: Judger error on test %d: %v", i, err)
			finalResponse.FinalStatus = models.StatusInternalError
			return finalResponse, err
		}
		
		// 3. Формирование результата для теста
		// FIX: Теперь judgerResult — это models.JudgerResponse
		testResult := models.TestResult{ 
			ID: tc.ID,
			Status: judgerResult.Status,
			IsPassed: judgerResult.Status == models.StatusAccepted,
			ActualOutput: judgerResult.ActualOutput,
			ExecutionTimeMs: judgerResult.ExecutionTimeMs,
			MemoryUsedMB: judgerResult.MemoryUsedMB,
			Details: judgerResult.Details,
		}
		finalResponse.TestResults = append(finalResponse.TestResults, testResult)

		// 4. Обновление общих метрик
		if judgerResult.ExecutionTimeMs > maxTime { maxTime = judgerResult.ExecutionTimeMs }
		if judgerResult.MemoryUsedMB > maxMemory { maxMemory = judgerResult.MemoryUsedMB }

		// 5. Обновление финального статуса (выбор самого "строгого")
		if testResult.Status != models.StatusAccepted {
			if testResult.Status == models.StatusCompileError || testResult.Status == models.StatusRuntimeError {
				finalStatus = testResult.Status
				finalResponse.ErrorMessage = testResult.Details
				break 
			}
			
			if finalStatus == models.StatusAccepted { 
				finalStatus = testResult.Status
			}
		}
	}
	
	// 6. Завершение итогового ответа
	finalResponse.FinalStatus = finalStatus
	finalResponse.MaxTimeMs = maxTime
	finalResponse.MaxMemoryMB = maxMemory
	
	return finalResponse, nil
}