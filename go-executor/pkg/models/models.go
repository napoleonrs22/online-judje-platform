package models

// --- СТАТУСЫ ---
const (
	StatusAccepted      = "ACCEPTED"
	StatusWrongAnswer   = "WRONG_ANSWER"
	StatusTimeLimit     = "TIME_LIMIT"
	StatusMemoryLimit   = "MEMORY_LIMIT"
	StatusRuntimeError  = "RUNTIME_ERROR"
	StatusCompileError  = "COMPILE_ERROR"
	StatusInternalError = "INTERNAL_ERROR"
)

// --- ТИПЫ ЧЕКЕРА (ДОБАВЛЕНО) ---
const (
	CheckerTypeExact  = "exact"
	CheckerTypeTokens = "tokens"
)

// --- Входные данные (Payload от FastAPI) ---

type TestCaseInput struct {
	ID              string `json:"id"`
	InputData       string `json:"input_data"`
	ExpectedOutput  string `json:"expected_output"`
}

type ExecutionRequest struct {
	SubmissionID      string          `json:"submission_id"`
	Language          string          `json:"language"`
	Code              string          `json:"code"`
	TimeLimit         int             `json:"time_limit"` // ms (фиксировано в FastAPI)
	MemoryLimit       int             `json:"memory_limit"` // MB (фиксировано в FastAPI)
	CheckerType       string          `json:"checker_type"`
	CustomCheckerCode *string         `json:"custom_checker_code"` // Может быть null
	TestCases         []TestCaseInput `json:"test_cases"`
}

// --- ТИПЫ ДЛЯ ВНУТРЕННЕГО ВЗАИМОДЕЙСТВИЯ (Judger/Service) ---

// JudgerRequest - Модель запроса для одного прогона теста
type JudgerRequest struct {
	Language string
	Code string
	TimeLimit int // ms
	MemoryLimit int // MB
	CheckerType string
	InputData string // Входные данные
	ExpectedOutput string // Ожидаемый вывод
}

// JudgerResponse - Модель ответа после проверки одного теста
type JudgerResponse struct {
	Status string
	ActualOutput string
	ExecutionTimeMs int
	MemoryUsedMB int
	Details string
}

// --- Выходные данные (Response в FastAPI) ---

// TestResult - результат одного тестового примера
type TestResult struct {
	ID              string `json:"id"`
	Status          string `json:"status"`
	IsPassed        bool   `json:"is_passed"`
	ActualOutput    string `json:"actual_output"`
	ExecutionTimeMs int    `json:"execution_time_ms"`
	MemoryUsedMB    int    `json:"memory_used_mb"`
	Details         string `json:"details"` 
}

type ExecutionResponse struct {
	SubmissionID    string       `json:"submission_id"`
	FinalStatus     string       `json:"final_status"`
	MaxTimeMs       int          `json:"max_time_ms"`
	MaxMemoryMB     int          `json:"max_memory_mb"`
	ErrorMessage    string       `json:"error_message"`
	TestResults     []TestResult `json:"test_results"`
}