# Architectural Decisions Record (ADR)

## Назначение
Документирование важных архитектурных и дизайн-решений.
Помогает будущим сессиям понять ПОЧЕМУ были сделаны определённые выборы.

---

## Decisions Log

### 2025-12-06 - Структура Task CLI

**Status:** Accepted

**Context:**
Нужен простой проект для тестирования Claude Code Kit workflow.

**Decision:**
Создать минималистичный CLI на Python:
- `src/cli.py` — точка входа, argparse
- `src/storage.py` — работа с JSON файлом
- `src/task.py` — модель Task
- `tests/` — pytest тесты

**Alternatives Considered:**
1. Web API — слишком сложно для теста
2. GUI — не подходит для CLI тестирования
3. Полноценный TODO app — overkill

**Consequences:**
- ✅ Быстрая реализация (< 100 строк)
- ✅ Все операции CRUD
- ✅ Легко тестировать
- ⚠️ Не production-ready (для тестов это OK)

---

