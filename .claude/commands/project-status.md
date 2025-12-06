---
description: Показывает текущий статус проекта. Использовать для быстрого обзора, при вопросах "что дальше", "где мы", или "status". Поддерживает компактный режим.
allowed-tools: Read, Bash, Grep, Glob
---
# Project Status

> `$ARGUMENTS`:
> - `compact` или `short` — краткий вывод
> - пусто — полный статус

Покажи текущий статус проекта.

## Context Discovery

При вызове СНАЧАЛА (с timeout для безопасности):

```bash
# 1. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null | head -15 || echo "No active task"

# 2. Git status (быстро)
timeout 5 git status --short 2>/dev/null | head -10

# 3. Тесты (quick check - только список)
timeout 10 pytest --co -q 2>/dev/null | tail -5 || echo "Tests: unknown"
```

## Missing Files Handling

| Файл | Если отсутствует |
|------|------------------|
| features.json | Показать "No features tracked" |
| current-task.md | Показать "No active task" |
| progress.md | Показать "No history" |

**ВАЖНО:** Если директория `.claude-workspace/` НЕ существует:

```markdown
⚠️ Workspace не инициализирован

Запустите `/init-project` для инициализации:
- Создаст структуру .claude-workspace/
- Настроит файлы отслеживания
- Проверит конфигурацию проекта
```

## Gather Information

```bash
# 1. Текущая задача
TASK=$(cat .claude-workspace/current-task.md 2>/dev/null | head -20) || TASK="No active task"

# 2. Последний прогресс
PROGRESS=$(cat .claude-workspace/progress.md 2>/dev/null | tail -30) || PROGRESS="No history"

# 3. Git status
GIT_STATUS=$(git status --short 2>/dev/null)
GIT_LOG=$(git log --oneline -5 2>/dev/null)
GIT_BRANCH=$(git branch --show-current 2>/dev/null)

# 4. Тесты (quick check с timeout)
TEST_RESULT=$(timeout 30 pytest --co -q 2>&1 | tail -5 || echo "Tests not configured")

# 5. Features
FEATURES=$(cat .claude-workspace/features.json 2>/dev/null | jq -r '.features[] | "\(.status): \(.name)"' 2>/dev/null) || FEATURES="No features tracked"
```

## Output Format

### If COMPACT mode (`$ARGUMENTS` contains "compact" or "short"):

```markdown
## Status (compact)

**Task:** [task name or "None"]
**Progress:** [X/Y steps]
**Branch:** `[branch]`
**Changes:** [uncommitted count or "clean"]
**Tests:** OK/FAIL

**Next:** [recommended action]
```

### If FULL mode (default):

```markdown
## Project Status

**Generated:** [timestamp]

---

### Current Task
[Из current-task.md или "No active task"]

**Progress:** [X/Y steps completed]
**Next Step:** [следующий незавершённый шаг]

---

### Recent Activity
[Последние 5 записей из progress.md]

---

### Features Overview

| Status | Feature |
|--------|---------|
| Done | feature1 |
| In Progress | feature2 |
| Planned | feature3 |

---

### Git Status

**Branch:** `[current branch]`

**Uncommitted Changes:**
[список файлов или "Working tree clean"]

**Recent Commits:**
1. `abc123` feat: description — 2h ago
2. `def456` fix: description — 5h ago
...

---

### Tests
```
[test output summary]
```
- Passing: X
- Failing: Y
- Coverage: Z% (if available)

---

### Warnings
[Any blockers, issues, or concerns]

---

### Recommended Next Steps

1. **[Most important action]**
   - Command: `/xxx`
2. [Second priority]
3. [Third priority]
```

## Quick Actions

После показа статуса, предложи релевантные команды:

| Ситуация | Рекомендация |
|----------|--------------|
| Workspace не создан | `/init-project` |
| Нет текущей задачи | `/plan [feature]` |
| Есть план, не начат | `/implement` |
| Есть изменения, готово | `/review` |
| Есть failed tests | `/test [feature]` |
| Есть uncommitted | `git add . && git commit` |

## Constraints

### ЗАПРЕЩЕНО
- Модифицировать файлы (read-only команда!)
- Запускать полные тесты (только --collect-only)
- Долгие операции без timeout

### ОБЯЗАТЕЛЬНО
- Использовать timeout для всех команд
- Graceful handling если файлы отсутствуют
- Показать конкретный next step

## Output

Заверши сообщением:
```
Suggested: [команда] — [почему]
```
