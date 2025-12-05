#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Твой токен (админа или студента — работает любой)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzY4ODBkMmUtNjBiNC00MDk2LTgzZTQtNmQyYTBjMzFlYjAzIiwidG9rZW5fdHlwZSI6ImFjY2VzcyIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NDMyMTI4Mywic3ViIjoiYzY4ODBkMmUtNjBiNC00MDk2LTgzZTQtNmQyYTBjMzFlYjAzIn0._8fqd9oRFm4F6IVkBv6loJuRG_pJ30kxONddDEiNBdY"

BASE_URL="http://localhost:8000"

echo -e "${BLUE}╔═══════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ТЕСТ ФУНКЦИОНАЛА СТУДЕНТА     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════╝${NC}"
echo

# Функция отправки решения
send() {
    local code="$1"
    local comment="$2"
    echo -e "${YELLOW}$comment${NC}"
    curl -s -X POST "$BASE_URL/api/student/submissions" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
          \"submission_id\": \"$(uuidgen)\",
          \"problem_slug\": \"a-plus-b\",
          \"language\": \"python\",
          \"code\": \"$code\"
        }" | jq '.' 2>/dev/null || echo "Ответ сервера получен (без jq)"
    echo
}

# 1. ACCEPTED
send "a, b = map(int, input().split())\nprint(a + b)" \
     "[1/5] ПРАВИЛЬНОЕ решение → должно быть ACCEPTED"

# 2. WRONG ANSWER
send "print(42)" \
     "[2/5] НЕПРАВИЛЬНЫЙ ответ → должно быть WRONG ANSWER"

# 3. COMPILE ERROR
send "print(\"Hello\"  # забыли скобку" \
     "[3/5] Синтаксическая ошибка → COMPILE ERROR"

# 4. RUNTIME ERROR
send "print(1 // 0)" \
     "[4/5] Деление на ноль → RUNTIME ERROR"

# 5. TIME LIMIT EXCEEDED
send "while True: pass" \
     "[5/5] Бесконечный цикл → TIME LIMIT EXCEEDED"

echo -e "${GREEN}╔═══════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ВСЕ 5 РЕШЕНИЙ ОТПРАВЛЕНЫ!        ║${NC}"
echo -e "${GREEN}║   Через 10–20 сек иди во фронтенд →${NC}"
echo -e "${GREEN}║   вкладка «Мои решения»           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════╝${NC}"