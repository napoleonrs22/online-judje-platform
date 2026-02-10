package http

import (
	"encoding/json"
	"go-executor/internal/domain"
	"log"
	"net/http"
)

type Handler struct {
	Service domain.JudgeService
	JobQueue chan domain.ExecutionRequest
}

func NewHandler(svc domain.JudgeService, workers int) *Handler {
	h := &Handler{
		Service:  svc,
		JobQueue: make(chan domain.ExecutionRequest, 100), // Буфер на 100 задач
	}

	// Запуск воркеров
	for i := 0; i < workers; i++ {
		go h.worker(i)
	}

	return h
}

// Воркер обрабатывает очередь, но в данной архитектуре (синхронный ответ)
// нам нужно немного другое.
// ТАК КАК PYTHON ЖДЕТ ОТВЕТА (async/await), мы не можем просто кинуть в канал и забыть.
// Нам нужен механизм "Ticket" или "Future", но это усложнит код.
//
// ПРОСТОЕ РЕШЕНИЕ: Семафор.
// Вместо явной очереди задач, мы используем буферизированный канал как семафор,
// чтобы ограничить количество одновременных go-рутин.

func (h *Handler) ExecuteHandler(w http.ResponseWriter, r *http.Request) {
	var req domain.ExecutionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 1. Пытаемся занять слот в очереди (Семафор)
	select {
	case h.JobQueue <- req:
		// Слот занят, продолжаем выполнение
		defer func() { <-h.JobQueue }() // Освобождаем слот при выходе
	default:
		// Очередь забита
		http.Error(w, "Server too busy", http.StatusServiceUnavailable)
		return
	}

	log.Printf("Received Submission: %s [%s]", req.SubmissionID, req.Language)

	// 2. Выполнение (Синхронно, но количество параллельных ограничено каналом)
	result := h.Service.Execute(r.Context(), req)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// Пустой worker не нужен при подходе с семафором,
// но если переходить на Webhooks, тогда worker нужен.
func (h *Handler) worker(id int) {
	// Placeholder for async architecture
}