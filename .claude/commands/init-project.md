---
description: Инициализация workspace проекта для Claude Code. Создаёт файлы отслеживания, структуру workspace и валидирует конфигурацию. Запускать один раз в начале проекта.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
# Initialize Project for Claude Code

Инициализируй проект для эффективной работы с Claude Code.

## Context Discovery

При вызове СНАЧАЛА проверь что уже существует:

```bash
# 1. Существующий workspace
ls -la .claude-workspace/ 2>/dev/null && echo "Workspace exists!"

# 2. Существующая конфигурация Claude
ls -la .claude/ 2>/dev/null && echo "Claude config exists!"

# 3. CLAUDE.md
cat CLAUDE.md 2>/dev/null | head -20 && echo "CLAUDE.md exists!"

# 4. Git status
git status --short 2>/dev/null || echo "Not a git repo"
```

## Pre-existing Files Check

| Файл | Если существует |
|------|-----------------|
| .claude-workspace/ | Спросить: merge или skip? |
| CLAUDE.md | Merge секции, не перезаписывать |
| .gitignore | Append только новые строки |
| .claude/ | Оставить как есть |

## Process

### 1. Analyze Project

```bash
# Определи тип проекта
echo "=== Project Analysis ==="
ls -la

# Tech stack
if [ -f "package.json" ]; then
  echo "Node.js project detected"
  cat package.json | jq '.name, .scripts'
elif [ -f "pyproject.toml" ]; then
  echo "Python project detected"
  cat pyproject.toml | head -20
elif [ -f "Cargo.toml" ]; then
  echo "Rust project detected"
elif [ -f "go.mod" ]; then
  echo "Go project detected"
else
  echo "Unknown project type"
fi

# Existing Claude config
if [ -d ".claude" ]; then
  echo "Existing .claude/ directory found"
  ls -la .claude/
fi
```

### 2. Create Workspace Structure

```bash
# Create directories
mkdir -p .claude-workspace
mkdir -p .claude/commands
mkdir -p .claude/agents
```

### 3. Create Tracking Files

#### .claude-workspace/progress.md
```markdown
# Progress Log

## Как использовать
- Добавляй запись в НАЧАЛЕ сессии с планируемой задачей
- Добавляй запись в КОНЦЕ сессии с результатами
- Храни последние 20 сессий, старые архивируй

---

## Session: [YYYY-MM-DD HH:MM]
**Task:** Инициализация проекта
**Completed:**
- Создана структура .claude-workspace
- Инициализированы файлы отслеживания
**Notes:** Готов к разработке

---
```

#### .claude-workspace/features.json
```json
{
  "project": "[PROJECT_NAME]",
  "lastUpdated": "[ISO_DATE]",
  "features": []
}
```

#### .claude-workspace/current-task.md
```markdown
# Current Task

No active task.

Use `/plan [feature]` to start planning a new feature.
```

#### .claude-workspace/decisions.md
```markdown
# Architectural Decisions

## Как использовать
Документируй важные решения:
- **Контекст:** Почему возникла необходимость решения?
- **Решение:** Что было выбрано и почему?
- **Последствия:** Какие последствия?

---

## [DATE] - Инициализация проекта

**Контекст:** Настройка Claude Code workflow для проекта.

**Решение:** Использование стандартной структуры .claude-workspace с TDD workflow.

**Последствия:** Вся команда будет следовать консистентному процессу разработки.

---
```

### 4. Create/Update CLAUDE.md

If CLAUDE.md doesn't exist, create basic one:

```markdown
# Project: [NAME]

## Tech Stack
- [detected tech stack]

## Commands
- `npm run dev` — start dev server
- `npm test` — run tests
- `npm run lint` — run linter

## Code Style
- [auto-detect from config files]

## Architecture
- [brief description]

## Important Notes
- [any critical info]
```

### 5. Validate Settings

```bash
# Check for hooks configuration
if [ ! -f ".claude/settings.json" ] && [ ! -f ".claude/settings.local.json" ]; then
  echo "No hooks configured. Consider adding .claude/settings.json"
fi

# Check for agents
if [ -z "$(ls -A .claude/agents/ 2>/dev/null)" ]; then
  echo "No custom agents. Consider adding agents to .claude/agents/"
fi
```

### 6. Git Setup (Idempotent)

```bash
# Add to .gitignore if needed (idempotent - проверяем перед добавлением)
grep -q "CLAUDE.local.md" .gitignore 2>/dev/null || echo "CLAUDE.local.md" >> .gitignore
grep -q "settings.local.json" .gitignore 2>/dev/null || echo ".claude/settings.local.json" >> .gitignore

# Initial commit (только если есть изменения)
if [ -n "$(git status --porcelain .claude-workspace/ .claude/ CLAUDE.md .gitignore 2>/dev/null)" ]; then
  git add .claude-workspace/ .claude/ CLAUDE.md .gitignore 2>/dev/null
  git commit -m "chore: initialize Claude Code workspace"
else
  echo "No changes to commit"
fi
```

## Error Handling

| Ошибка | Действие |
|--------|----------|
| No write permissions | Предупредить и остановиться |
| Directory exists | Спросить пользователя: skip или overwrite |
| Git not initialized | Предложить `git init` |
| Files modified | Предупредить о перезаписи |

## Constraints

### ЗАПРЕЩЕНО
- Перезаписывать существующие файлы без спроса
- Добавлять дубликаты в .gitignore
- Коммитить без проверки что есть изменения

### ОБЯЗАТЕЛЬНО
- Проверить существование перед созданием
- Использовать idempotent команды
- Спрашивать при конфликтах

## Output

```markdown
## ✅ Project Initialized for Claude Code

### Created Structure
```
.claude-workspace/
├── progress.md      ✅
├── features.json    ✅
├── current-task.md  ✅
└── decisions.md     ✅

.claude/
├── agents/              [X agents]
├── commands/            [X commands]
└── settings.local.json  [exists/missing]
```

### CLAUDE.md
[Created/Updated/Already exists and valid]

### Git
[Initial commit created / Already tracked]

---

### 🚀 Next Steps

1. Review and customize `CLAUDE.md` for your project
2. Run `/project-status` to see current state
3. Run `/plan [first feature]` to start development

### 💡 Recommended Commands
- `/project-status` — check project state
- `/plan [feature]` — plan a new feature
- `/quick-fix [bug]` — fix small bugs
```