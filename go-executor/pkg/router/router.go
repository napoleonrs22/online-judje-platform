// go-executor/pkg/router/router.go

package router

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"go-executor/pkg/models"
	"go-executor/pkg/service"
)

// Router - Структура для маршрутизации
type Router struct {
	SubmissionService service.SubmissionService
}

func NewRouter(ss service.SubmissionService) *Router {
	return &Router{SubmissionService: ss}
}

// RegisterRoutes - Регистрация маршрутов
func (r *Router) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("/execute", r.executeHandler)
}

// executeHandler - Обработчик POST-запроса от FastAPI
func (r *Router) executeHandler(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		http.Error(w, "Только метод POST разрешен", http.StatusMethodNotAllowed)
		return
	}

	var executionRequest models.ExecutionRequest
	if err := json.NewDecoder(req.Body).Decode(&executionRequest); err != nil {
		http.Error(w, "Некорректный JSON-запрос: " + err.Error(), http.StatusBadRequest)
		return
	}
    
    log.Printf("Router: Received submission %s for language %s", 
        executionRequest.SubmissionID, executionRequest.Language)

	// Используем контекст запроса
	ctx := context.Background() 
	
	// 1. Вызываем сервис для выполнения кода
	response, err := r.SubmissionService.JudgeSubmission(ctx, executionRequest)
	
	if err != nil {
		log.Printf("Router: Internal execution error for %s: %v", executionRequest.SubmissionID, err)
		http.Error(w, models.StatusInternalError + ": " + err.Error(), http.StatusInternalServerError)
		return
	}

	// 2. Отправляем JSON-ответ обратно в FastAPI
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}