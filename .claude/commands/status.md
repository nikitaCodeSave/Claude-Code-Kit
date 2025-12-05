---
description: Shows current project status. Use for quick overview, when user asks "what's next", "where are we", or "status". Supports compact mode.
allowed-tools: Read, Bash, Grep, Glob
---
# Project Status

Покажи текущий статус проекта.

## Arguments

`$ARGUMENTS`:
- `compact` или `short` — краткий вывод (только essentials)
- пусто — полный статус

## Gather Information

```bash
# 1. Текущая задача
TASK=$(cat .claude-workspace/current-task.md 2>/dev/null | head -20)

# 2. Последний прогресс
PROGRESS=$(cat .claude-workspace/progress.md 2>/dev/null | tail -30)

# 3. Git status
GIT_STATUS=$(git status --short 2>/dev/null)
GIT_LOG=$(git log --oneline -5 2>/dev/null)
GIT_BRANCH=$(git branch --show-current 2>/dev/null)

# 4. Тесты (quick check)
TEST_RESULT=$(timeout 30 npm test 2>&1 | tail -5 || echo "Tests not configured")

# 5. Features
FEATURES=$(cat .claude-workspace/features.json 2>/dev/null | jq -r '.features[] | "\(.status): \(.name)"' 2>/dev/null)
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
   - Command: `/project:xxx`
2. [Second priority]
3. [Third priority]
```

## Quick Actions

После показа статуса, предложи релевантные команды:

| Ситуация | Рекомендация |
|----------|--------------|
| Нет текущей задачи | `/project:plan [feature]` |
| Есть план, не начат | `/project:implement` |
| Есть изменения, готово | `/project:review` |
| Есть failed tests | `/project:test [feature]` |
| Есть uncommitted | `git add . && git commit` |

## Output

Заверши сообщением:
```
Suggested: [команда] — [почему]
```
