# Current Task

## Task: Add Task Command (F001)

### Objective
Реализовать CLI команду `task add "title"` для добавления новой задачи в JSON хранилище.

### Complexity: S (Small)
### Estimated Steps: 3
### Risk Level: Low

---

### Scope

**In Scope:**
- Модель Task с полями id, title, done, created_at
- Storage класс для работы с JSON файлом
- CLI команда `add` через argparse
- Юнит-тесты для всех компонентов

**Out of Scope:**
- Команды list, done, delete (отдельные фичи)
- Валидация ввода (пустой title)
- Конфигурация пути к файлу

---

### Implementation Steps

#### 1. [x] **Step 1: Task Model + Tests** ✅
   - **Files:** `src/task.py`, `tests/test_task.py`
   - **Changes:**
     - Dataclass Task с полями: id (uuid), title (str), done (bool=False), created_at (datetime)
     - Методы to_dict() и from_dict()
   - **Tests:**
     - test_task_creation
     - test_task_to_dict
     - test_task_from_dict
   - **Estimated time:** 10 min

#### 2. [x] **Step 2: Storage + Tests** ✅
   - **Files:** `src/storage.py`, `tests/test_storage.py`
   - **Changes:**
     - Class TaskStorage с методами: load(), save(), add_task()
     - Хранение в ~/.tasks.json (или tasks.json в cwd)
   - **Tests:**
     - test_storage_add_task
     - test_storage_persistence (save/load)
   - **Estimated time:** 10 min

#### 3. [x] **Step 3: CLI + Integration Test** ✅
   - **Files:** `src/cli.py`, `tests/test_cli.py`
   - **Changes:**
     - argparse с subcommand `add`
     - main() function как entry point
   - **Tests:**
     - test_cli_add_task (integration)
   - **Estimated time:** 10 min

---

### Files to Create
- `src/task.py` — Task dataclass model
- `src/storage.py` — JSON storage handler
- `src/cli.py` — CLI entry point
- `tests/test_task.py` — Task model tests
- `tests/test_storage.py` — Storage tests
- `tests/test_cli.py` — CLI integration tests

### Files to Modify
- `src/__init__.py` — exports (optional)

### Dependencies
- None (stdlib only: json, uuid, datetime, argparse, dataclasses)

---

### Success Criteria
- [x] `python -m src.cli add "Buy milk"` создаёт задачу
- [x] Задача сохраняется в tasks.json
- [x] Все тесты проходят: `pytest tests/ -v` (11 tests)
- [x] Код чистый, без warnings

---

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| File permissions | Использовать try/except при записи |
| JSON corruption | Atomic write (write to temp, then rename) |

---

### TDD Order
```
RED    → test_task_creation fails (no Task class)
GREEN  → implement Task dataclass
RED    → test_storage_add_task fails (no Storage)
GREEN  → implement TaskStorage
RED    → test_cli_add_task fails (no cli.py)
GREEN  → implement CLI
REFACTOR → cleanup, docstrings
```
