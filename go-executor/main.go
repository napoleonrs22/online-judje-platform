package main

import (
	"log"
	"net/http"
	"fmt"
	"go-executor/pkg/router"
	"go-executor/pkg/service"
	"go-executor/pkg/judger"
)

const listenPort = "8001"

func main() {
	// 1. Инициализация Judger (связь с Docker)
	judger, err := judger.NewDockerJudger()
	if err != nil {
		log.Fatalf("Ошибка инициализации Judger (Docker): %v", err)
	}

	// 2. Инициализация Сервиса (бизнес-логика)
	submissionService := service.NewSubmissionService(judger)

	// 3. Инициализация Роутера (HTTP-взаимодействие)
	appRouter := router.NewRouter(submissionService)

	// 4. Регистрация маршрутов
	mux := http.NewServeMux()
	appRouter.RegisterRoutes(mux)

	// 5. Запуск сервера
	serverAddr := fmt.Sprintf(":%s", listenPort)
	log.Printf("🔥 Go Code Executor запущен на порту %s", serverAddr)
	
	err = http.ListenAndServe(serverAddr, mux)
	if err != nil {
		log.Fatalf("Ошибка при запуске сервера: %v", err)
	}
}