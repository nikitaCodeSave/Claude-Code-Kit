---
description: Завершает текущую задачу. Архивирует план, обновляет features.json, очищает current-task.md. Использовать после одобрения /code-review.
allowed-tools: Read, Write, Edit, Bash, Grep
---
# Завершение задачи

Заверши текущую задачу и архивируй результаты.

## Сбор контекста

При вызове СНАЧАЛА:

```bash
# 1. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null | head -20

# 2. Git status
git status --short 2>/dev/null

# 3. Последние коммиты
git log --oneline -5 2>/dev/null

# 4. Статус features.json
cat .claude-workspace/features.json 2>/dev/null | head -30
```

## Валидация

### 1. Проверь наличие задачи

```bash
TASK_CONTENT=$(cat .claude-workspace/current-task.md 2>/dev/null)
```

Если файл пустой или содержит "No active task" / "Нет активной задачи":
> ERROR: Нет активной задачи для завершения. Создайте задачу с `/create-plan`.

### 2. Проверь завершённость шагов

Посчитай шаги в current-task.md:
- Всего шагов: `grep -c "^\s*[0-9]\+\.\s*\[" .claude-workspace/current-task.md`
- Выполнено: `grep -c "^\s*[0-9]\+\.\s*\[x\]" .claude-workspace/current-task.md`

Если не все шаги отмечены [x]:
> WARNING: Выполнено N из M шагов. Продолжить завершение? Незавершённые шаги будут отмечены как пропущенные.

### 3. Проверь git status

```bash
git status --porcelain
```

Если есть незакоммиченные изменения:
> WARNING: Есть незакоммиченные изменения. Рекомендуется закоммитить перед завершением.

## Процесс завершения

### 1. Извлеки данные

```bash
# Название задачи (из первой строки с ## Задача: или ## Task:)
TASK_NAME=$(grep -E "^## (Задача|Task):" .claude-workspace/current-task.md | head -1 | sed 's/^## \(Задача\|Task\): //')

# Если не найдено, возьми первый заголовок ##
if [ -z "$TASK_NAME" ]; then
  TASK_NAME=$(grep "^## " .claude-workspace/current-task.md | head -1 | sed 's/^## //')
fi

# Slug для архива (kebab-case)
SLUG=$(echo "$TASK_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 50)

# Дата
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
```

### 2. Создай архив

Путь: `.claude-workspace/archive/${DATE}-${SLUG}.md`

Содержимое архива:

```markdown
# Archived Task: [TASK_NAME]

**Completed:** [TIMESTAMP]
**Status:** DONE

---

[ПОЛНЫЙ КОНТЕНТ current-task.md]

---

## Completion Summary

### Коммиты за период задачи
[git log --oneline --since="1 week ago" | head -10]

### Изменённые файлы
[git diff --stat HEAD~5 2>/dev/null | tail -10]
```

### 3. Обнови features.json

Найди фичу по имени задачи и обнови:

```json
{
  "status": "done",
  "completedAt": "[ISO timestamp]",
  "updatedAt": "[ISO timestamp]",
  "archivePath": ".claude-workspace/archive/[DATE]-[SLUG].md"
}
```

Если фича не найдена — создай новую запись со статусом "done".

### 4. Обнови progress.md

Добавь в НАЧАЛО файла (после заголовка # Progress):

```markdown
## [COMPLETED] [TIMESTAMP] - [TASK_NAME]

### Summary
- **Шаги:** [выполнено]/[всего]
- **Коммиты:** [количество за неделю]
- **Архив:** `.claude-workspace/archive/[DATE]-[SLUG].md`

### Результат
[Список выполненных шагов из current-task.md]

---
```

### 5. Очисти current-task.md

Замени содержимое на:

```markdown
# Current Task

Нет активной задачи.

## Quick Start
1. `/create-plan [feature]` — создать план
2. `/implement` — реализовать по плану
3. `/code-review` — код-ревью
4. `/complete-task` — завершить и архивировать

## Last Completed
- **Задача:** [TASK_NAME]
- **Дата:** [DATE]
- **Архив:** `.claude-workspace/archive/[DATE]-[SLUG].md`
```

## Формат вывода

```markdown
## Задача завершена

**Название:** [TASK_NAME]
**Дата:** [TIMESTAMP]

### Архивировано
`.claude-workspace/archive/[DATE]-[SLUG].md`

### Обновлено
- features.json: status → "done"
- progress.md: добавлена запись [COMPLETED]
- current-task.md: очищен

### Статистика
- Шаги: [выполнено]/[всего]
- Коммиты: [N]

---

**Следующие шаги:**
- `/create-plan [новая фича]` — начать новую задачу
- `/project-status` — посмотреть обзор проекта
```

## Ограничения

### ЗАПРЕЩЕНО
- Удалять задачу без архивации
- Перезаписывать существующие архивы (добавь суффикс -2, -3 если существует)

### ОБЯЗАТЕЛЬНО
- Сохранить ПОЛНЫЙ контент задачи в архив
- Обновить ВСЕ tracking файлы
- Показать summary после завершения
