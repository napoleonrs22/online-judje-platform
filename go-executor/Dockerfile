# go-executor/Dockerfile

# 1. Builder Stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Кэшируем зависимости
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходный код
COPY . .

# ВАЖНО: Путь к main.go изменился в новой архитектуре
RUN go build -o executor cmd/executor/main.go

# 2. Final Stage
FROM alpine:latest

# Устанавливаем docker-cli (иногда полезно для отладки внутри контейнера)
# и совместимые библиотеки
RUN apk add --no-cache ca-certificates docker-cli

WORKDIR /app

# Копируем бинарник из билдера
COPY --from=builder /app/executor .

# Создаем папку для временных файлов (она должна совпадать с volume в docker-compose)
RUN mkdir -p /tmp/judger

# Указываем переменную окружения по умолчанию
ENV JUDGER_SHARED_DIR=/tmp/judger
ENV PORT=8001

# Запуск
CMD ["./executor"]