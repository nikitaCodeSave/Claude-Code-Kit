# Project Status

Покажи текущий статус проекта.

## Gather Information

```bash
# 1. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null || echo "No current task"

# 2. Прогресс
cat .claude-workspace/progress.md 2>/dev/null | tail -50

# 3. Фичи
cat .claude-workspace/features.json 2>/dev/null || echo "No features file"

# 4. Git status
git status --short
git log --oneline -5

# 5. Тесты (quick check)
npm run test 2>/dev/null || pytest --collect-only 2>/dev/null || echo "Tests not configured"
```

## Output Format

```markdown
## 📊 Project Status

**Generated:** [timestamp]

---

### 🎯 Current Task
[Из current-task.md или "No active task"]

**Progress:** [X/Y steps completed]

---

### 📝 Recent Activity
[Последние 5 записей из progress.md]

---

### 📦 Features Overview

| Status | Count | Features |
|--------|-------|----------|
| ✅ Done | X | feature1, feature2 |
| 🔄 In Progress | Y | feature3 |
| ⏳ Pending | Z | feature4, feature5 |

---

### 🔀 Git Status

**Branch:** `[current branch]`
**Uncommitted changes:** [yes/no - list files if yes]

**Recent commits:**
1. [hash] [message] - [time ago]
2. ...

---

### 🧪 Tests
- Total: X
- Passing: Y
- Failing: Z

---

### ⚠️ Warnings/Issues
- [Any blockers or issues]

---

### 📌 Recommended Next Steps

1. [Most important next action]
2. [Second priority]
3. [Third priority]
```

## Quick Actions
После показа статуса, предложи:
- `/project:plan [feature]` - если нет текущей задачи
- `/project:implement` - если есть план
- `/project:review` - если есть незакоммиченные изменения
- `/project:test [feature]` - если нужно тестирование
