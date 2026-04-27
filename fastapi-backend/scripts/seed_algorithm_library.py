"""
Библиотека готовых алгоритмических задач для платформы.

Запуск (локально, из папки fastapi-backend, с DATABASE_URL в .env):
  python scripts/seed_algorithm_library.py

Через Docker (если смонтирован каталог backend):
  docker compose exec api python scripts/seed_algorithm_library.py

Пропускает slug, если задача с таким slug уже есть.
Автор — первый пользователь с ролью teacher или admin, иначе любой первый user.
Все задачи создаются с is_public=True (видны всем студентам).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from src.database import AsyncSessionLocal  # noqa: E402
from src.models.base import CheckerType, DifficultyLevel  # noqa: E402
from src.models.user_models import User  # noqa: E402
from src.repository.problem_repository import ProblemRepository  # noqa: E402
from src.schemas.schemas import ExampleCreate, ProblemCreate, TestCaseCreate  # noqa: E402

# User ссылается на Group; без этого импорта mapper падает с KeyError: 'Group'
from src.models import group_models  # noqa: F401, E402


def ex(inp: str, out: str, expl: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"input_data": inp, "output_data": out}
    if expl:
        d["explanation"] = expl
    return d


def tc(inp: str, out: str, sample: bool = False) -> dict[str, Any]:
    return {"input_data": inp, "output_data": out, "is_sample": sample}


LIBRARY: list[dict[str, Any]] = [
    # ——— Ввод-вывод, база ———
    {
        "title": "A + B (шаблон ввода)",
        "slug": "lib-io-a-plus-b",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: ввод-вывод]** Даны два целых числа в одной строке через пробел. "
            "Выведите их сумму."
        ),
        "examples": [ex("2 3", "5")],
        "tests": [
            tc("2 3", "5", True),
            tc("0 0", "0", False),
            tc("-5 12", "7", False),
            tc("1000000 1000000", "2000000", False),
        ],
    },
    {
        "title": "Минимум из двух чисел",
        "slug": "lib-io-min-two",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: условия]** В одной строке через пробел даны два целых числа a и b. "
            "Выведите min(a, b)."
        ),
        "examples": [ex("4 7", "4")],
        "tests": [
            tc("4 7", "4", True),
            tc("10 3", "3", False),
            tc("-2 -5", "-5", False),
        ],
    },
    {
        "title": "Чётность числа",
        "slug": "lib-io-parity",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: арифметика]** Дано целое n. Выведите EVEN, если чётное, иначе ODD."
        ),
        "examples": [ex("4", "EVEN")],
        "tests": [
            tc("4", "EVEN", True),
            tc("7", "ODD", False),
            tc("0", "EVEN", False),
        ],
    },
    {
        "title": "НОД двух чисел",
        "slug": "lib-math-gcd",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: математика / Евклид]** Даны a и b (неотрицательные, не оба нули). "
            "Выведите наибольший общий делитель."
        ),
        "examples": [ex("48 18", "6")],
        "tests": [
            tc("48 18", "6", True),
            tc("7 1", "1", False),
            tc("100 25", "25", False),
        ],
    },
    {
        "title": "НОК двух чисел",
        "slug": "lib-math-lcm",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: математика]** Даны положительные целые a и b. Выведите их НОК."
        ),
        "examples": [ex("4 6", "12")],
        "tests": [
            tc("4 6", "12", True),
            tc("3 5", "15", False),
            tc("12 18", "36", False),
        ],
    },
    # ——— Массивы ———
    {
        "title": "Сумма элементов массива",
        "slug": "lib-array-sum",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: массивы]** Первая строка: n. Вторая строка: n целых чисел через пробел. "
            "Выведите сумму всех элементов."
        ),
        "examples": [ex("3\n1 2 3", "6")],
        "tests": [
            tc("3\n1 2 3", "6", True),
            tc("1\n-5", "-5", False),
            tc("4\n0 0 0 0", "0", False),
        ],
    },
    {
        "title": "Максимум в массиве",
        "slug": "lib-array-max",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: массивы]** Первая строка: n. Вторая: n чисел. Выведите максимум."
        ),
        "examples": [ex("4\n3 1 4 1", "4")],
        "tests": [
            tc("4\n3 1 4 1", "4", True),
            tc("1\n-10", "-10", False),
            tc("5\n0 0 0 0 0", "0", False),
        ],
    },
    {
        "title": "Разворот массива",
        "slug": "lib-array-reverse",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: массивы / два указателя]** n и массив. Выведите элементы в обратном порядке через пробел."
        ),
        "examples": [ex("3\n1 2 3", "3 2 1")],
        "tests": [
            tc("3\n1 2 3", "3 2 1", True),
            tc("1\n7", "7", False),
            tc("4\n-1 0 2 5", "5 2 0 -1", False),
        ],
    },
    # ——— Два указателя / окна ———
    {
        "title": "Палиндром строки",
        "slug": "lib-two-pointers-palindrome",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: два указателя / строки]** Дана строка из строчных латинских букв (без пробелов). "
            "Выведите YES, если палиндром, иначе NO."
        ),
        "examples": [ex("abba", "YES")],
        "tests": [
            tc("abba", "YES", True),
            tc("abc", "NO", False),
            tc("a", "YES", False),
            tc("racecar", "YES", False),
        ],
    },
    {
        "title": "Два числа в отсортированном массиве (сумма)",
        "slug": "lib-two-pointers-two-sum-sorted",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: два указателя]** Первая строка: n и target через пробел. "
            "Вторая: n неубывающих целых чисел. "
            "Если есть два разных индекса i < j с a[i]+a[j]==target, выведите i и j через пробел (0-индексация). "
            "Иначе выведите NO."
        ),
        "examples": [ex("6 10\n1 2 3 4 5 6", "3 5", "Индексы 3 и 5: 4+6=10")],
        "tests": [
            tc("6 10\n1 2 3 4 5 6", "3 5", True),
            tc("3 100\n1 2 3", "NO", False),
            tc("2 8\n4 4", "0 1", False),
        ],
    },
    # ——— Хеш / множества ———
    {
        "title": "Анаграммы",
        "slug": "lib-hash-anagram",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: хеш / сортировка символов]** Две строки из строчных латинских букв. "
            "YES, если анаграммы, иначе NO."
        ),
        "examples": [ex("listen\nsilent", "YES")],
        "tests": [
            tc("listen\nsilent", "YES", True),
            tc("hello\nworld", "NO", False),
            tc("a\na", "YES", False),
        ],
    },
    {
        "title": "Первое повторяющееся число",
        "slug": "lib-hash-first-duplicate",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: хеш]** Первая строка: n. Вторая: n целых чисел. "
            "Выведите первое число, которое встречается второй раз при чтении слева направо. "
            "Если повторов нет, выведите NO."
        ),
        "examples": [ex("5\n1 2 3 2 4", "2")],
        "tests": [
            tc("5\n1 2 3 2 4", "2", True),
            tc("3\n1 2 3", "NO", False),
            tc("4\n7 7 1 2", "7", False),
        ],
    },
    # ——— Бинарный поиск ———
    {
        "title": "Позиция в отсортированном массиве",
        "slug": "lib-binary-search-index",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: бинарный поиск]** Первая строка: n и x. Вторая: n строго возрастающих целых чисел. "
            "Выведите индекс x (0-индексация) или -1, если нет."
        ),
        "examples": [ex("5 7\n1 3 5 7 9", "3")],
        "tests": [
            tc("5 7\n1 3 5 7 9", "3", True),
            tc("3 2\n1 3 5", "-1", False),
            tc("1 10\n10", "0", False),
        ],
    },
    {
        "title": "Целая часть квадратного корня",
        "slug": "lib-binary-search-isqrt",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: бинарный поиск]** Дано неотрицательное целое n. Выведите ⌊√n⌋."
        ),
        "examples": [ex("17", "4")],
        "tests": [
            tc("17", "4", True),
            tc("0", "0", False),
            tc("15", "3", False),
            tc("100", "10", False),
        ],
    },
    # ——— Префиксные суммы ———
    {
        "title": "Сумма на отрезке (prefix sums)",
        "slug": "lib-prefix-range-sum",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: префиксные суммы]** Строка 1: n. Строка 2: n целых чисел. Строка 3: q — число запросов. "
            "Далее q строк: l r — границы отрезка (0-индексация, включительно). "
            "Для каждого запроса выведите сумму на отрезке на отдельной строке."
        ),
        "examples": [
            ex(
                "5\n1 2 3 4 5\n3\n0 2\n1 3\n0 4",
                "6\n9\n15",
            )
        ],
        "tests": [
            tc("5\n1 2 3 4 5\n3\n0 2\n1 3\n0 4", "6\n9\n15", True),
            tc("1\n10\n1\n0 0", "10", False),
            tc("3\n-1 0 2\n1\n0 2", "1", False),
        ],
    },
    # ——— Строки ———
    {
        "title": "Разворот строки",
        "slug": "lib-string-reverse",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: строки]** Одна строка (без перевода строки внутри). Выведите её в обратном порядке."
        ),
        "examples": [ex("hello", "olleh")],
        "tests": [
            tc("hello", "olleh", True),
            tc("a", "a", False),
            tc("12345", "54321", False),
        ],
    },
    {
        "title": "Корректные скобки",
        "slug": "lib-stack-brackets",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: стек]** Строка из символов ( ) [ ]. Выведите YES, если скобки корректны, иначе NO."
        ),
        "examples": [ex("()", "YES")],
        "tests": [
            tc("()", "YES", True),
            tc("([)]", "NO", False),
            tc("[]()", "YES", False),
            tc("((", "NO", False),
        ],
    },
    # ——— DP простое ———
    {
        "title": "Числа Фибоначчи",
        "slug": "lib-dp-fibonacci",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: DP / рекуррентность]** Дано n (0 ≤ n ≤ 30). F(0)=0, F(1)=1. Выведите F(n)."
        ),
        "examples": [ex("10", "55")],
        "tests": [
            tc("10", "55", True),
            tc("0", "0", False),
            tc("1", "1", False),
            tc("20", "6765", False),
        ],
    },
    {
        "title": "Лестница: количество способов",
        "slug": "lib-dp-climbing-stairs",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: DP]** n ступенек. За раз 1 или 2 ступени. Сколько различных способов допрыгнуть до n? "
            "(n от 1 до 30.)"
        ),
        "examples": [ex("5", "8")],
        "tests": [
            tc("5", "8", True),
            tc("1", "1", False),
            tc("2", "2", False),
            tc("10", "89", False),
        ],
    },
    {
        "title": "Монеты: минимальное число купюр",
        "slug": "lib-dp-coin-min",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: DP]** Строка 1: сумма S. Строка 2: k и k номиналов монет через пробел (все положительные). "
            "Неограниченное число монет каждого номинала. Выведите минимальное число монет для S, "
            "или -1 если невозможно. (S ≤ 100, k ≤ 10, номиналы ≤ 50.)"
        ),
        "examples": [ex("6\n3 1 3 4", "2", "6 = 3+3")],
        "tests": [
            tc("6\n3 1 3 4", "2", True),
            tc("3\n1 2", "-1", False),
            tc("7\n2 2 5", "2", False),
        ],
    },
    # ——— Жадность ———
    {
        "title": "Максимум из пар (жадность на массиве пар)",
        "slug": "lib-greedy-max-pairs",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: жадность / сортировка]** Первая строка: n. Далее n строк: a_i b_i — отрезки [a_i, b_i] целые. "
            "Выберите максимальное число непересекающихся отрезков (если касаются концом — пересекаются). "
            "Жадность: после сортировки по правому концу. Выведите одно число — максимальное количество."
        ),
        "examples": [ex("3\n1 3\n2 4\n3 5", "1", "Все пересекаются попарно в простом примере — оставляем один")],
        "tests": [
            tc("3\n1 3\n2 4\n3 5", "1", True),
            tc("3\n1 2\n2 3\n3 4", "2", False),
            tc("1\n0 10", "1", False),
        ],
    },
    # ——— Битовые / логика ———
    {
        "title": "XOR всех чисел",
        "slug": "lib-bit-xor-array",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: биты]** n и n целых чисел. Выведите XOR всех элементов."
        ),
        "examples": [ex("3\n1 2 3", "0")],
        "tests": [
            tc("3\n1 2 3", "0", True),
            tc("1\n42", "42", False),
            tc("4\n5 5 7 7", "0", False),
        ],
    },
    {
        "title": "Количество единичных битов",
        "slug": "lib-bit-popcount",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: биты]** Дано неотрицательное целое n (n ≤ 10^9). Выведите число единиц в двоичной записи."
        ),
        "examples": [ex("7", "3")],
        "tests": [
            tc("7", "3", True),
            tc("0", "0", False),
            tc("8", "1", False),
        ],
    },
    # ——— Скользящее окно / сортировка ———
    {
        "title": "Максимальная сумма подмассива длины k",
        "slug": "lib-sliding-window-max-sum",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: скользящее окно]** Строка 1: n и k (1 ≤ k ≤ n ≤ 10^5). Строка 2: n целых чисел. "
            "Выведите максимальную сумму подотрезка ровно из k подряд идущих элементов."
        ),
        "examples": [ex("5 2\n1 -2 3 4 -1", "7", "Окно 3+4")],
        "tests": [
            tc("5 2\n1 -2 3 4 -1", "7", True),
            tc("3 1\n5 -1 2", "5", False),
            tc("4 4\n1 1 1 1", "4", False),
        ],
    },
    {
        "title": "Число различных элементов",
        "slug": "lib-set-distinct-count",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: множество / сортировка]** n и n целых чисел. Выведите количество различных значений."
        ),
        "examples": [ex("5\n1 2 2 3 1", "3")],
        "tests": [
            tc("5\n1 2 2 3 1", "3", True),
            tc("1\n0", "1", False),
            tc("4\n7 7 7 7", "1", False),
        ],
    },
    {
        "title": "НОД всего массива",
        "slug": "lib-math-gcd-array",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: математика]** n (1 ≤ n ≤ 100) и n положительных целых чисел. Выведите НОД всех элементов."
        ),
        "examples": [ex("3\n12 18 24", "6")],
        "tests": [
            tc("3\n12 18 24", "6", True),
            tc("1\n17", "17", False),
            tc("2\n7 5", "1", False),
        ],
    },
    {
        "title": "Отсортировать и вывести",
        "slug": "lib-sort-print",
        "difficulty": DifficultyLevel.EASY,
        "description": (
            "**[Тема: сортировка]** n и n целых чисел. Выведите их в неубывающем порядке через пробел."
        ),
        "examples": [ex("4\n4 1 3 2", "1 2 3 4")],
        "tests": [
            tc("4\n4 1 3 2", "1 2 3 4", True),
            tc("1\n-5", "-5", False),
            tc("3\n0 0 0", "0 0 0", False),
        ],
    },
    {
        "title": "k-я порядковая статистика (малые n)",
        "slug": "lib-sort-kth-smallest",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": (
            "**[Тема: сортировка / выбор]** Строка 1: n и k (1 ≤ k ≤ n ≤ 5000). Строка 2: n целых чисел (могут повторяться). "
            "Выведите k-й элемент в **неубывающей** сортировке (k=1 — минимальный)."
        ),
        "examples": [ex("5 3\n7 1 5 2 2", "2", "Отсортировано: 1 2 2 5 7")],
        "tests": [
            tc("5 3\n7 1 5 2 2", "2", True),
            tc("1 1\n42", "42", False),
            tc("4 2\n4 3 2 1", "2", False),
        ],
    },
]


async def resolve_author_id(session) -> UUID:
    stmt = (
        select(User.id)
        .where(User.role.in_(["teacher", "admin"]))
        .order_by(User.created_at.asc())
        .limit(1)
    )
    r = await session.execute(stmt)
    row = r.first()
    if row:
        return row[0]
    r2 = await session.execute(select(User.id).order_by(User.created_at.asc()).limit(1))
    row2 = r2.first()
    if not row2:
        raise RuntimeError(
            "В базе нет пользователей. Создайте учителя/админа и повторите запуск."
        )
    return row2[0]


async def main() -> None:
    created = 0
    skipped = 0
    async with AsyncSessionLocal() as session:
        repo = ProblemRepository(session)
        author_id = await resolve_author_id(session)

        for spec in LIBRARY:
            if await repo.check_slug_exists(spec["slug"]):
                skipped += 1
                print(f"  skip (exists): {spec['slug']}")
                continue

            examples = [ExampleCreate(**ex) for ex in spec["examples"]]
            tests = [TestCaseCreate(**t) for t in spec["tests"]]
            pc = ProblemCreate(
                title=spec["title"],
                slug=spec["slug"],
                description=spec["description"],
                difficulty=spec["difficulty"],
                checker_type=CheckerType.EXACT,
                examples=examples,
                test_cases=tests,
                is_public=True,
                assigned_student_ids=[],
            )
            dump = pc.model_dump(exclude={"test_cases", "examples"})
            dump["user_id"] = author_id
            examples_data = [e.model_dump() for e in pc.examples]
            test_cases_data = [t.model_dump() for t in pc.test_cases]

            await repo.create_problem(dump, examples_data, test_cases_data)
            created += 1
            print(f"  + {spec['slug']}")

    print(f"\nГотово: создано {created}, пропущено (уже есть) {skipped}, всего в каталоге {len(LIBRARY)}.")


if __name__ == "__main__":
    asyncio.run(main())
