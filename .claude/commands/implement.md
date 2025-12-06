---
description: Реализует текущую задачу из .claude-workspace/current-task.md через строгий TDD. Использовать после одобрения плана.
allowed-tools: Read, Edit, MultiEdit, Write, Bash, Grep, Glob
---
# Implement Current Task

Реализуй задачу из `.claude-workspace/current-task.md` следуя TDD.

## Context Discovery

При вызове СНАЧАЛА:

```bash
# 1. Текущий план
cat .claude-workspace/current-task.md 2>/dev/null || echo "ERROR: No plan. Run /plan first."

# 2. Git status
git status --short 2>/dev/null

# 3. Tech stack
cat pyproject.toml 2>/dev/null | head -15 || cat package.json 2>/dev/null | head -15

# 4. Baseline тесты
pytest --co -q 2>/dev/null | tail -5 || echo "No tests found"
```

## Pre-Implementation Checklist

```bash
# 1. Проверь что план существует
if [ ! -f .claude-workspace/current-task.md ]; then
  echo "ERROR: No plan found. Run /plan first."
  exit 1
fi

# 2. Покажи текущую задачу
cat .claude-workspace/current-task.md

# 3. Проверь прогресс
cat .claude-workspace/progress.md 2>/dev/null | tail -20

# 4. Проверь git status
git status --short

# 5. Убедись что тесты проходят (baseline)
pytest -v 2>&1 | tail -10
```

## Implementation Process

### Для КАЖДОГО шага из плана:

#### 1. Write Test FIRST (RED)

```python
# Создай тест описывающий expected behavior
def test_feature_expected_behavior():
    result = feature_function(input_data)
    assert result == expected_output
```

```bash
# Запусти - он ДОЛЖЕН УПАСТЬ
pytest tests/test_feature.py::test_feature_expected_behavior -v
```

#### 2. Write Minimal Code (GREEN)

```bash
# Напиши минимум кода для прохождения теста
# Запусти - ДОЛЖЕН ПРОЙТИ
pytest tests/test_feature.py -v
```

#### 3. Refactor (если нужно)

```bash
# Улучши код без изменения поведения
# Тесты ВСЁ ЕЩЁ должны проходить
pytest tests/ -v
ruff check src/ --fix
```

#### 4. Commit
```bash
git add .
git commit -m "type(scope): description

Step X/Y of [task-id]"
```

#### 5. Update Tracking
- Отметь `[x]` выполненный шаг в `current-task.md`
- Добавь запись в `progress.md`

## After All Steps Completed

```bash
# 1. Все тесты
pytest tests/ -v

# 2. Linting
ruff check src/

# 3. Type checking (если используется mypy)
mypy src/ 2>/dev/null || echo "mypy not configured"

# 4. Coverage
pytest --cov=src --cov-report=term-missing 2>/dev/null | tail -20
```

## Error Recovery

| Ситуация | Действие |
|----------|----------|
| Тест не проходит > 15 мин | Спросить пользователя, записать в progress.md |
| План неверен | Вернуться к /plan, обновить план |
| Dependency conflict | Документировать в decisions.md, решить |
| Flaky test | Пометить `@pytest.mark.flaky`, исследовать |
| Build fails | Исправить до продолжения |

## Timing Constraints

- Один шаг: максимум **30 минут**
- Весь implement: максимум **2 часа**
- Если дольше → декомпозировать задачу

## Completion Checklist

- [ ] Все шаги плана выполнены
- [ ] Все тесты проходят
- [ ] Linting без ошибок
- [ ] Нет `console.log` в production коде
- [ ] `progress.md` обновлён
- [ ] `current-task.md` все шаги отмечены
- [ ] Код закоммичен

## Constraints

### ЗАПРЕЩЕНО
- Пропускать написание тестов
- Коммитить нерабочий код
- Менять план без согласования
- Работать над несколькими шагами одновременно
- Оставлять `print()` / `console.log` в production

### ОБЯЗАТЕЛЬНО
- Каждый шаг = один атомарный коммит
- Обновить progress.md после каждого шага
- Запускать все тесты перед коммитом
- Спрашивать если застрял > 15 минут

## Quality Checklist

Перед завершением проверь:

- [ ] Все тесты проходят (`pytest tests/ -v`)
- [ ] Linting без ошибок (`ruff check src/`)
- [ ] Нет `print()` в production коде
- [ ] Coverage не снизился
- [ ] Все шаги плана отмечены как выполненные
- [ ] progress.md обновлён
- [ ] Коммиты атомарны и описательны

## Output

После завершения покажи:
```markdown
## Implementation Complete

### Files Changed
- `src/module.py` — [description]
- `src/utils.py` — [description]

### Tests Added
- `tests/test_module.py` — [what it tests]

### Git Log
[последние N коммитов]

### Следующие шаги
- [ ] Запусти /review для код-ревью
- [ ] Или продолжи со следующей задачей
```