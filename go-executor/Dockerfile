# go-executor/Dockerfile

# 1. Используем Go в качестве базового образа для сборки (Builder Stage)
FROM golang:1.23-alpine AS builder 

WORKDIR /app

# Копируем go.mod и go.sum для загрузки зависимостей
COPY go.mod .
COPY go.sum .
RUN go mod download

# Копируем исходный код
COPY . .

# Собираем приложение
RUN go build -o /go-executor main.go

# -------------------------------------------------------------
# 2. Используем минимальный образ для финального развертывания (Final Stage)
FROM alpine:latest

# Устанавливаем ca-certificates 
RUN apk add --no-cache ca-certificates 
# 🔥 УДАЛЕНА: установка docker-cli
# 🔥 УДАЛЕНА: команда RUN docker pull...

WORKDIR /usr/bin

# Копируем скомпилированный бинарник
COPY --from=builder /go-executor /go-executor

# Устанавливаем точку входа
ENTRYPOINT ["/go-executor"]