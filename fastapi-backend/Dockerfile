# fastapi-backend/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Установка клиента PostgreSQL для команды pg_isready
RUN apt-get update && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта
COPY . .

# Запуск приложения с Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]