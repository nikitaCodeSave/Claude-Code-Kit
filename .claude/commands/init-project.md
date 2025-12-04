# Initialize Project for Claude Code

Инициализируй проект для эффективной работы с Claude Code.

## Process

### 1. Анализ проекта
Изучи структуру проекта:
```bash
ls -la
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || cat requirements.txt 2>/dev/null
```

### 2. Создай workspace директорию
```bash
mkdir -p .claude-workspace
```

### 3. Создай tracking файлы

#### progress.md
```markdown
# Progress Log

## How to Use
- Add entry at START of each session with task
- Add entry at END of each session with results
- Keep last 20 sessions, archive older

---

## Session: [YYYY-MM-DD HH:MM]
- **Started:** [timestamp]
- **Task:** Project initialization
- **Completed:** 
  - Created .claude-workspace structure
  - Initialized tracking files
- **Notes:** Ready for development

---
```

#### features.json
```json
{
  "project": "[PROJECT_NAME]",
  "lastUpdated": "[ISO_DATE]",
  "features": []
}
```

#### current-task.md
```markdown
# Current Task

No active task. Use `/project:plan [feature]` to start.
```

#### decisions.md
```markdown
# Architectural Decisions

## How to Use
Document important decisions with:
- Context: Why was this decision needed?
- Decision: What was decided?
- Consequences: What are the implications?

---

## [DATE] - Decision Title

**Context:** ...

**Decision:** ...

**Consequences:** ...

---
```

### 4. Проверь/обнови CLAUDE.md
Если CLAUDE.md не существует или неполный:
- Определи tech stack
- Определи основные команды
- Определи code style
- Создай или обнови файл

### 5. Проверь .claude/commands/
Убедись что базовые команды существуют:
- plan.md
- implement.md
- review.md
- test.md
- fix-issue.md
- status.md

### 6. Git setup
```bash
# Добавь в .gitignore если нужно
echo "CLAUDE.local.md" >> .gitignore
echo ".claude/settings.local.json" >> .gitignore

# Initial commit для workspace
git add .claude-workspace/
git add .claude/commands/
git add CLAUDE.md
git commit -m "chore: initialize Claude Code workspace"
```

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

.claude/commands/
├── plan.md          ✅
├── implement.md     ✅
├── review.md        ✅
├── test.md          ✅
├── fix-issue.md     ✅
└── status.md        ✅
```

### CLAUDE.md
[Created/Updated/Already exists]

### Next Steps
1. Review and customize CLAUDE.md for your project
2. Run `/project:status` to see current state
3. Run `/project:plan [first feature]` to start development
```
