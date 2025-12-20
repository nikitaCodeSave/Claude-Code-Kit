---
description: Завершает текущую задачу. Архивирует в archive/, обновляет state.json. Использовать после /review с вердиктом APPROVED.
allowed-tools: Read, Write, Edit, Bash, Grep
---

# /done

Заверши текущую задачу и архивируй результаты.

## ШАГ 1: Валидация

```bash
# 1. Есть ли активная задача?
cat .claude-workspace/state.json | jq '.currentTask'

# 2. Git status
git status --short

# 3. Последние коммиты
git log --oneline -5
```

**Если currentTask == null:**
> ERROR: Нет активной задачи. Создайте с `/plan-task [feature]`.

**Если есть незакоммиченные изменения:**
> WARNING: Есть незакоммиченные изменения. Закоммитьте перед завершением.

## ШАГ 2: Проверка завершённости

```bash
# Посчитай шаги
TOTAL=$(cat .claude-workspace/state.json | jq '.currentTask.steps | length')
COMPLETED=$(cat .claude-workspace/state.json | jq '[.currentTask.steps[] | select(.completed)] | length')

echo "Completed: $COMPLETED / $TOTAL"
```

**Если не все шаги завершены:**
> WARNING: Выполнено $COMPLETED из $TOTAL шагов. Продолжить? Незавершённые шаги будут отмечены как пропущенные.

## ШАГ 3: Создание архива

```bash
# Извлечь данные
TASK_NAME=$(cat .claude-workspace/state.json | jq -r '.currentTask.name')
TASK_ID=$(cat .claude-workspace/state.json | jq -r '.currentTask.id')
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date -Iseconds)

# Slug для файла
SLUG=$(echo "$TASK_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 50)

# Путь архива
ARCHIVE_PATH=".claude-workspace/archive/${DATE}-${SLUG}.md"
```

**Создать файл архива:**

```markdown
# Archived Task: [TASK_NAME]

**Completed:** [TIMESTAMP]
**Task ID:** [TASK_ID]
**Status:** DONE

---

## Task Details

[Данные из state.json.currentTask в Markdown формате]

### Steps
[Список шагов с отметками completed]

### Success Criteria
[Критерии успеха]

---

## Completion Summary

### Commits
[git log --oneline за период задачи]

### Changed Files
[git diff --stat]

### Test Results
[Последний результат тестов]
```

## ШАГ 4: Обновление state.json

```json
{
  "currentTask": null,
  "features": [
    {
      "id": "[TASK_ID]",
      "name": "[TASK_NAME]",
      "status": "done",
      "completedAt": "[TIMESTAMP]",
      "archivePath": "[ARCHIVE_PATH]"
    }
  ],
  "progress": [
    {
      "timestamp": "[TIMESTAMP]",
      "type": "COMPLETE",
      "taskId": "[TASK_ID]",
      "message": "Completed: [TASK_NAME]"
    }
  ]
}
```

**Изменения:**
1. `currentTask` = null
2. Найти feature по id → обновить status = "done", добавить completedAt и archivePath
3. Добавить запись в progress[]

## ШАГ 5: Git commit (опционально)

Если есть изменения в state.json:

```bash
git add .claude-workspace/
git commit -m "chore(workspace): complete task [TASK_NAME]

- Archived to [ARCHIVE_PATH]
- Updated state.json
- Task ID: [TASK_ID]"
```

## Формат вывода

```markdown
## Task Completed

**Name:** [TASK_NAME]
**ID:** [TASK_ID]
**Date:** [TIMESTAMP]

### Archived
`[ARCHIVE_PATH]`

### Updated
- state.json: currentTask → null
- features[]: status → "done"
- progress[]: +1 COMPLETE entry

### Stats
- Steps: [completed]/[total]
- Commits: [N]
- Files changed: [M]

---

**Next Steps:**
- `/plan-task [new feature]` — start new task
- `cat .claude-workspace/state.json | jq '.features'` — view all features
```

## Ограничения

### ❌ ЗАПРЕЩЕНО
- Удалять задачу без архивации
- Перезаписывать существующие архивы (добавь суффикс -2 если существует)
- Завершать без проверки незакоммиченных изменений

### ✅ ОБЯЗАТЕЛЬНО
- Сохранить полные данные задачи в архив
- Обновить state.json (currentTask = null)
- Показать summary после завершения
