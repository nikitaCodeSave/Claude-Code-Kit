---
description: Инициализация workspace проекта для Claude Code. Создаёт файлы отслеживания, структуру workspace и валидирует конфигурацию. Запускать один раз в начале проекта.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
# Инициализация проекта для Claude Code

Инициализируй проект для эффективной работы с Claude Code.

## ШАГ 0: Валидация окружения (ОБЯЗАТЕЛЬНО ПЕРВЫМ)

```bash
# Проверить права на запись
if [ ! -w "." ]; then
  echo "NO_WRITE_PERMISSION"
fi

# Проверить git
if [ ! -d ".git" ]; then
  echo "NOT_GIT_REPO"
fi
```

**Если `NO_WRITE_PERMISSION`:**
> **Нет прав на запись в директорию.**
>
> Проверьте права доступа или выберите другую директорию.
>
> **Прерываю выполнение.**

**Если `NOT_GIT_REPO`:**
> **Директория не является git репозиторием.**
>
> **Варианты:**
> 1. Инициализировать git: `git init` (рекомендуется)
> 2. Продолжить без git (скажите "продолжить")
> 3. Отмена (скажите "отмена")
>
> **Дождаться ответа пользователя.**

---

## ШАГ 1: Проверка существующего workspace

```bash
# Проверить существующий workspace
if [ -d ".claude-workspace" ]; then
  echo "WORKSPACE_EXISTS"
  ls -la .claude-workspace/
fi
```

**Если `WORKSPACE_EXISTS`:**
> **Найден существующий workspace:**
> ```
> [вывод ls -la]
> ```
>
> **Варианты:**
> 1. Пропустить создание workspace (скажите "skip")
> 2. Merge — добавить недостающие файлы (скажите "merge")
> 3. Перезаписать (скажите "overwrite") — данные будут потеряны
>
> **Дождаться ответа пользователя. НЕ продолжать автоматически.**

---

## ШАГ 2: Определение проекта

```bash
echo "=== Проект ==="
PROJECT_NAME=$(basename $(pwd))
echo "Проект: $PROJECT_NAME"

echo ""
echo "=== Структура ==="
tree -L 2 -I 'node_modules|__pycache__|.git|.venv|venv|dist|build' 2>/dev/null || ls -la
```

Сохранить `PROJECT_NAME` для использования в следующих шагах.

---

## ШАГ 3: Создание структуры директорий

```bash
# Создать директории (идемпотентно)
mkdir -p .claude-workspace
mkdir -p .claude-workspace/archive
mkdir -p .claude/commands
mkdir -p .claude/agents

echo "Директории созданы:"
ls -la .claude-workspace/
ls -la .claude/
```

---

## ШАГ 4: Создание файлов отслеживания

### 4.1 progress.md

**Создать если не существует:**

```markdown
# Лог прогресса

## Как использовать
- Записывай в НАЧАЛО файла (новые записи сверху)
- Формат: `## [YYYY-MM-DD HH:MM] - [Тип]: [Описание]`
- Типы: PLAN, IMPLEMENT, FIX, REVIEW, COMPLETE

---

## [DATE] - INIT: Инициализация проекта
- Создана структура .claude-workspace
- Готов к разработке

---
```

### 4.2 features.json

**Создать если не существует:**

```json
{
  "project": "[PROJECT_NAME]",
  "lastUpdated": "[ISO_DATE]",
  "features": []
}
```

### 4.3 current-task.md

**Создать если не существует:**

```markdown
# Текущая задача

Нет активной задачи.

## Быстрый старт
1. `/create-plan [feature]` — создать план
2. `/implement` — реализовать по плану
3. `/code-review` — код-ревью
4. `/complete-task` — завершить и архивировать
```

### 4.4 decisions.md

**Создать если не существует:**

```markdown
# Архитектурные решения (ADR)

## Формат записи

> **ADR-NNN: [Название]**
> - Дата: YYYY-MM-DD
> - Статус: Принято / Отменено / Заменено ADR-XXX
> - Контекст -> Решение -> Последствия

---

## ADR-001: Инициализация Claude Code Workflow

**Дата:** [DATE]
**Статус:** Принято

### Контекст
Необходимо стандартизировать процесс разработки с Claude Code.

### Решение
Использование структуры .claude-workspace с TDD workflow.

### Последствия
- [+] Консистентный процесс разработки
- [+] Отслеживание прогресса и решений
- [-] Дополнительные файлы в репозитории

---
```

---

## ШАГ 5: Проверка CLAUDE.md

```bash
if [ -f "CLAUDE.md" ]; then
  echo "CLAUDE_MD_EXISTS"
else
  echo "NO_CLAUDE_MD"
fi
```

**Если `CLAUDE_MD_EXISTS`:**
> CLAUDE.md найден. Продолжаю.

**Если `NO_CLAUDE_MD`:**
> **CLAUDE.md не найден.**
>
> Рекомендую запустить `/init` после завершения инициализации —
> он проанализирует проект и создаст качественное описание.
>
> Продолжаю без CLAUDE.md.

---

## ШАГ 6: Настройка .gitignore

```bash
# Добавить записи идемпотентно
grep -qxF "CLAUDE.local.md" .gitignore 2>/dev/null || echo "CLAUDE.local.md" >> .gitignore
grep -qxF ".claude/settings.local.json" .gitignore 2>/dev/null || echo ".claude/settings.local.json" >> .gitignore

echo ".gitignore обновлён"
```

---

## ШАГ 7: Валидация результата

```bash
echo "=== Валидация ==="

# Проверить все файлы
check_file() {
  if [ -f "$1" ]; then
    echo "OK $1"
  else
    echo "MISSING $1"
  fi
}

check_file ".claude-workspace/progress.md"
check_file ".claude-workspace/features.json"
check_file ".claude-workspace/current-task.md"
check_file ".claude-workspace/decisions.md"

# CLAUDE.md опционален
if [ -f "CLAUDE.md" ]; then
  echo "OK CLAUDE.md"
else
  echo "INFO CLAUDE.md не найден — запустите /init для создания"
fi

# Проверить settings
if [ -f ".claude/settings.json" ] || [ -f ".claude/settings.local.json" ]; then
  echo "OK Settings configured"
else
  echo "INFO No settings.json — consider adding hooks configuration"
fi

# Проверить agents и commands
AGENT_COUNT=$(ls -1 .claude/agents/*.md 2>/dev/null | wc -l)
CMD_COUNT=$(ls -1 .claude/commands/*.md 2>/dev/null | wc -l)
echo "Agents: $AGENT_COUNT"
echo "Commands: $CMD_COUNT"
```

**Если какой-то файл MISSING:**
> **Не все файлы созданы.**
>
> Отсутствуют: [список]
>
> Попробовать создать повторно?

---

## ШАГ 8: Git коммит (опционально)

```bash
# Проверить наличие изменений
if [ -n "$(git status --porcelain .claude-workspace/ .claude/ CLAUDE.md .gitignore 2>/dev/null)" ]; then
  echo "CHANGES_DETECTED"
  git status --short .claude-workspace/ .claude/ CLAUDE.md .gitignore
else
  echo "NO_CHANGES"
fi
```

**Если `CHANGES_DETECTED`:**
> **Обнаружены изменения для коммита:**
> ```
> [git status --short]
> ```
>
> **Закоммитить изменения?** (да/нет)

**При подтверждении:**
```bash
git add .claude-workspace/ .claude/ .gitignore
git commit -m "chore: initialize Claude Code workspace

- Add .claude-workspace/ tracking files
- Add progress.md, features.json, current-task.md
- Configure .gitignore for local files"
```

---

## Формат вывода

```markdown
## Проект инициализирован

**Проект:** [PROJECT_NAME]
**Дата:** [DATE]

---

### Созданная структура

```
.claude-workspace/
├── progress.md      OK
├── features.json    OK
├── current-task.md  OK
├── decisions.md     OK
└── archive/         OK

.claude/
├── agents/          [X файлов]
└── commands/        [X файлов]
```

### Файлы конфигурации

| Файл | Статус |
|------|--------|
| CLAUDE.md | Существует / Нет (запустите /init) |
| .gitignore | Обновлён |
| settings.json | Есть / Нет |

### Git

| Действие | Статус |
|----------|--------|
| Коммит | Создан / Пропущен |

---

## Следующие шаги

1. **Создайте CLAUDE.md** — запустите `/init` если файл отсутствует
2. **Запустите `/project-status`** — убедитесь что всё работает
3. **Начните разработку** — `/create-plan [первая фича]`

### Доступные команды

| Команда | Описание |
|---------|----------|
| `/project-status` | Текущее состояние проекта |
| `/create-plan` | Спланировать новую фичу |
| `/quick-fix` | Быстрое исправление бага |
| `/implement` | Реализовать по плану |
```

---

## Ограничения

### ЗАПРЕЩЕНО
- Перезаписывать файлы без явного подтверждения пользователя
- Добавлять дубликаты в .gitignore
- Коммитить без проверки наличия изменений
- Продолжать при ошибке валидации (ШАГ 0)

### ОБЯЗАТЕЛЬНО
- Проверить права и git статус первым шагом
- Спрашивать при существующих файлах
- Использовать идемпотентные команды
- Показать итоговую валидацию

---

## Обработка ошибок

| Ошибка | Шаг | Действие |
|--------|-----|----------|
| Нет прав записи | 0 | СТОП, сообщить пользователю |
| Не git repo | 0 | Спросить: init или продолжить |
| Workspace существует | 1 | Спросить: skip/merge/overwrite |
| Файл не создался | 7 | Повторить создание |
| Git commit failed | 8 | Предупредить, продолжить |
