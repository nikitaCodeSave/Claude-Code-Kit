---
description: Реализует текущую задачу из state.json через TDD. Использовать после /plan.
allowed-tools: Read, Edit, MultiEdit, Write, Bash, Grep, Glob, Task
---

# /implement

Реализует задачу из `state.json.currentTask` используя TDD-подход.

## ШАГ 1: Context Discovery

```bash
# 1. Текущая задача
cat .claude-workspace/state.json | jq '.currentTask'

# 2. Git status
git status --short

# 3. Существующие тесты
pytest --co -q 2>/dev/null | tail -5 || npm test -- --listTests 2>/dev/null | tail -5
```

**Если currentTask == null:**
> ERROR: Нет плана. Создайте с `/plan [feature]`.

## ШАГ 2: Обновить статус

Обновить state.json:
```json
{
  "currentTask": {
    "status": "in_progress"
  }
}
```

## ШАГ 3: Делегировать dev-agent

**ОБЯЗАТЕЛЬНО** используй Task tool для делегирования dev-agent:

```
[Task: dev-agent]
prompt: |
  ## Задача: Реализация по плану

  ### Контекст
  - План: state.json.currentTask
  - Шаги: state.json.currentTask.steps

  ### Инструкции
  1. Загрузи план из .claude-workspace/state.json
  2. Для каждого шага выполни TDD цикл:
     - Write test (RED)
     - Write code (GREEN)
     - Refactor
     - Commit
     - Update state.json (step.completed = true)
  3. Атомарные коммиты после каждого шага
  4. Обновляй state.json.progress[]

  ### Ограничения
  - Один шаг = один коммит
  - Тест сначала ПАДАЕТ, потом ПРОХОДИТ
  - Код всегда в рабочем состоянии
```

Дождись завершения dev-agent.

## ШАГ 4: Финальные проверки

```bash
# Все тесты
pytest tests/ -v || npm test

# Linting
ruff check src/ || npm run lint

# Type checking
mypy src/ 2>/dev/null || npm run typecheck 2>/dev/null

# Coverage
pytest --cov=src --cov-report=term-missing 2>/dev/null | tail -20
```

## ШАГ 5: Обновить статус

Обновить state.json:
```json
{
  "currentTask": {
    "status": "review"
  },
  "progress": [
    {
      "timestamp": "[ISO timestamp]",
      "type": "IMPLEMENT",
      "taskId": "[currentTask.id]",
      "message": "Implementation complete. Ready for review."
    }
  ]
}
```

## Формат вывода

```markdown
## Implementation Complete

| Metric | Value |
|--------|-------|
| Steps completed | X/Y |
| Tests added | Z |
| Files changed | W |
| Commits | N |
| Coverage | M% |

### Completed Steps
[Список шагов из state.json]

### Git Log
[Последние коммиты]

### Status: READY_FOR_REVIEW

### Next Steps
- Запустите `/review` для код-ревью
```

## Ограничения

### ❌ ЗАПРЕЩЕНО
- Пропускать TDD цикл
- Коммитить нерабочий код
- Менять план без согласования
- Работать над несколькими шагами одновременно

### ✅ ОБЯЗАТЕЛЬНО
- Каждый шаг = один атомарный коммит
- Обновлять state.json после каждого шага
- Все тесты проходят перед коммитом
- Спрашивать если застрял > 15 минут
