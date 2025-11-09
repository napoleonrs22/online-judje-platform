#!/bin/sh
set -e

check_and_pull() {
    IMAGE_NAME="$1"

    IMAGE_ID=$(docker images -q "$IMAGE_NAME")
    if [ -n "$IMAGE_ID" ]; then
        echo "Образ $IMAGE_NAME уже существует. Пропускаем загрузку."
    else
        echo "Образ $IMAGE_NAME отсутствует. Начинаем загрузку..."
        docker pull "$IMAGE_NAME"
        if [ $? -eq 0 ]; then
            echo "Образ $IMAGE_NAME успешно загружен."
        else
            echo "Ошибка при загрузке образа $IMAGE_NAME. Проверьте подключение."
            exit 1
        fi
    fi
}

echo "Проверка и загрузка Docker образов..."

check_and_pull "python:3.10-slim"
check_and_pull "gcc:latest"
check_and_pull "eclipse-temurin:17-jdk-alpine"
check_and_pull "node:18-alpine"

echo "Все необходимые образы для Judger готовы!"
