package main

import (
	"go-executor/internal/delivery/http"
	"go-executor/internal/infrastructure/docker"
	"go-executor/internal/usecase"
	"log"
	netHttp "net/http"
	"os"

	"github.com/gorilla/mux"
)

func main() {
	// 1. Init Infrastructure
	dockerClient, err := docker.NewDockerExecutor()
	if err != nil {
		log.Fatalf("Failed to init docker client: %v", err)
	}
	log.Println("✅ Docker client connected")

	// 2. Init UseCase
	// DockerExecutor реализует и Compiler и Runner интерфейсы
	judgeService := usecase.NewJudgeService(dockerClient, dockerClient)

	// 3. Init Handler with Semaphore (Worker Pool Limit)
	// 5 = Максимум 5 одновременных проверок
	handler := http.NewHandler(judgeService, 5)

	// 4. Router
	r := mux.NewRouter()
	r.HandleFunc("/execute", handler.ExecuteHandler).Methods("POST")

	// 5. Start Server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8001"
	}

	log.Printf("🚀 Executor started on port %s", port)
	if err := netHttp.ListenAndServe(":"+port, r); err != nil {
		log.Fatal(err)
	}
}