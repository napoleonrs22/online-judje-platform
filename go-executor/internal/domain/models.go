package domain

import (
	"context"
)

// --- Models ---

type ExecutionRequest struct {
	SubmissionID string     `json:"submission_id"`
	Language     string     `json:"language"`
	Code         string     `json:"code"`
	TimeLimit    int        `json:"time_limit"`   // ms
	MemoryLimit  int        `json:"memory_limit"` // MB
	CheckerType  string     `json:"checker_type"`
	TestCases    []TestCase `json:"test_cases"`
}

type TestCase struct {
	ID             string `json:"id"`
	InputData      string `json:"input_data"`
	ExpectedOutput string `json:"expected_output"`
}

type ExecutionResponse struct {
	SubmissionID string       `json:"submission_id"`
	FinalStatus  string       `json:"final_status"`
	MaxTimeMs    int          `json:"max_time_ms"`
	MaxMemoryMB  int          `json:"max_memory_mb"`
	ErrorMessage string       `json:"error_message,omitempty"`
	TestResults  []TestResult `json:"test_results"`
}

type TestResult struct {
	ID              string `json:"id"`
	Status          string `json:"status"`
	ActualOutput    string `json:"actual_output"`
	ExecutionTimeMs int    `json:"execution_time_ms"`
	MemoryUsedMB    int    `json:"memory_used_mb"`

	// --- ДОБАВЛЕНЫ НОВЫЕ ПОЛЯ ДЛЯ FastAPI ---
	IsPassed        bool   `json:"is_passed"`
	Details         string `json:"details"`
}

// --- Interfaces ---

type Compiler interface {
	Compile(ctx context.Context, code, language, workDir string) (string, error)
}

type Runner interface {
	Run(ctx context.Context, binPath, language, workDir, inputData string, timeLimit, memLimit int) (TestResult, error)
	Cleanup(workDir string)
}

type JudgeService interface {
	Execute(ctx context.Context, req ExecutionRequest) ExecutionResponse
}