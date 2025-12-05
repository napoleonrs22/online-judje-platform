#!/bin/bash
set -e

BASE_URL="http://localhost:8000"
AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzY4ODBkMmUtNjBiNC00MDk2LTgzZTQtNmQyYTBjMzFlYjAzIiwidG9rZW5fdHlwZSI6ImFjY2VzcyIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NDMzNTc3OCwic3ViIjoiYzY4ODBkMmUtNjBiNC00MDk2LTgzZTQtNmQyYTBjMzFlYjAzIn0.EI1SYhheazoduwxBLGmS7gTa_C_FfxFlRemkKnCrVrE"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

create() {
    local payload="$1"
    echo -e "${YELLOW}Создаю задачу...${NC}"

    response=$(curl -s -X POST "$BASE_URL/api/teacher/problems" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")

    if echo "$response" | grep -q '"id"' >/dev/null 2>&1; then
        title=$(echo "$payload" | grep -o '"title":"[^"]*' | cut -d'"' -f4)
        id=$(echo "$response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        echo -e "${GREEN}ГОТОВО → $title (ID: $id)${NC}"
    else
        title=$(echo "$payload" | grep -o '"title":"[^"]*' | cut -d'"' -f4 2>/dev/null || echo "Неизвестная")
        echo -e "${RED}ОШИБКА → $title${NC}"
        echo "$response" | head -5
    fi
    echo
}

# 1. A + B
create '{
  "title": "A + B",
  "slug": "a-plus-b",
  "description": "Даны два целых числа. Выведите их сумму.",
  "input_format": "Два целых числа",
  "output_format": "Одно число — сумма",
  "difficulty": "Легкий",
  "time_limit": 1000,
  "memory_limit": 64,
  "examples": [
    {"input_data": "1 2", "output_data": "3", "is_hidden": false},
    {"input_data": "-5 8", "output_data": "3", "is_hidden": false}
  ],
  "test_cases": [
    {"input_data": "1 2", "output_data": "3", "is_hidden": false},
    {"input_data": "-5 8", "output_data": "3", "is_hidden": false},
    {"input_data": "0 0", "output_data": "0", "is_hidden": true},
    {"input_data": "1000000 1000000", "output_data": "2000000", "is_hidden": true}
  ]
}'

# 2. Привет, мир!
create '{
  "title": "Привет, мир!",
  "slug": "hello-world",
  "description": "Выведите строку Hello, World!",
  "input_format": "Нет",
  "output_format": "Hello, World!",
  "difficulty": "Легкий",
  "time_limit": 1000,
  "memory_limit": 64,
  "examples": [
    {"input_data": "", "output_data": "Hello, World!", "is_hidden": false}
  ],
  "test_cases": [
    {"input_data": "", "output_data": "Hello, World!", "is_hidden": false}
  ]
}'

# Остальные 8 задач — просто копипаста
create '{
  "title": "Реверс строки", "slug": "reverse-string", "description": "Разверните строку.",
  "input_format": "Одна строка", "output_format": "Реверс", "difficulty": "Легкий",
  "time_limit": 1000, "memory_limit": 64,
  "examples": [{"input_data": "hello", "output_data": "olleh", "is_hidden": false}],
  "test_cases": [
    {"input_data": "hello", "output_data": "olleh", "is_hidden": false},
    {"input_data": "abc", "output_data": "cba", "is_hidden": true}
  ]
}'

create '{
  "title": "Сортировка массива", "slug": "sort-array", "description": "Отсортируйте по возрастанию.",
  "input_format": "n\\nмассив", "output_format": "отсортированный массив", "difficulty": "Средний",
  "time_limit": 2000, "memory_limit": 128,
  "examples": [{"input_data": "5\n3 1 4 1 5", "output_data": "1 1 3 4 5", "is_hidden": false}],
  "test_cases": [{"input_data": "5\n3 1 4 1 5", "output_data": "1 1 3 4 5", "is_hidden": false}]
}'

create '{
  "title": "Факториал", "slug": "factorial", "description": "N!", "difficulty": "Средний",
  "time_limit": 1000, "memory_limit": 64,
  "examples": [{"input_data": "5", "output_data": "120", "is_hidden": false}],
  "test_cases": [{"input_data": "5", "output_data": "120", "is_hidden": false}]
}'

create '{
  "title": "FizzBuzz", "slug": "fizzbuzz", "description": "Классика", "difficulty": "Легкий",
  "time_limit": 1000, "memory_limit": 64,
  "examples": [{"input_data": "15", "output_data": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", "is_hidden": false}],
  "test_cases": [{"input_data": "15", "output_data": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", "is_hidden": false}]
}'

create '{
  "title": "Простое число?", "slug": "is-prime", "description": "YES / NO", "difficulty": "Средний",
  "time_limit": 2000, "memory_limit": 64,
  "examples": [{"input_data": "7", "output_data": "YES", "is_hidden": false}],
  "test_cases": [
    {"input_data": "7", "output_data": "YES", "is_hidden": false},
    {"input_data": "4", "output_data": "NO", "is_hidden": false}
  ]
}'

create '{
  "title": "Сумма матрицы", "slug": "matrix-sum", "description": "Сумма элементов", "difficulty": "Средний",
  "time_limit": 2000, "memory_limit": 128,
  "examples": [{"input_data": "2 2\n1 2\n3 4", "output_data": "10", "is_hidden": false}],
  "test_cases": [{"input_data": "2 2\n1 2\n3 4", "output_data": "10", "is_hidden": false}]
}'

create '{
  "title": "Фибоначчи", "slug": "fibonacci", "description": "N-е число", "difficulty": "Средний",
  "time_limit": 3000, "memory_limit": 256,
  "examples": [{"input_data": "10", "output_data": "55", "is_hidden": false}],
  "test_cases": [{"input_data": "10", "output_data": "55", "is_hidden": false}]
}'

create '{
  "title": "Бинарный поиск", "slug": "binary-search", "description": "Позиция или -1", "difficulty": "Сложный",
  "time_limit": 2000, "memory_limit": 128,
  "examples": [{"input_data": "5 7\n1 3 5 7 9", "output_data": "3", "is_hidden": false}],
  "test_cases": [{"input_data": "5 7\n1 3 5 7 9", "output_data": "3", "is_hidden": false}]
}'

echo -e "${GREEN}████████████████████████████████████████${NC}"
echo -e "${GREEN}    ВСЁ! 10 ЗАДАЧ УСПЕШНО В БАЗЕ!    ${NC}"
echo -e "${GREEN}    http://localhost:3000 → РЕШАЙ!       ${NC}"
echo -e "${GREEN}████████████████████████████████████████${NC}"