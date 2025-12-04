---
description: Creates detailed implementation plan for a feature or task. Use when user mentions "plan", "design", "architect", or before implementing any feature > 50 lines of code.
allowed-tools: Read, Grep, Glob, Bash
---
# Plan Feature/Task: $ARGUMENTS

Создай детальный план для задачи. **НЕ ПИШИ КОД.**

## Process

### 1. Explore (используй explore-agent для сложных задач)

```bash
# Изучи структуру проекта
tree -L 2 -I 'node_modules|__pycache__|.git' | head -40

# Найди похожие реализации
rg "similar_pattern" --type-add 'code:*.{ts,py,js}' -t code -l | head -10

# Проверь существующие паттерны
cat CLAUDE.md 2>/dev/null | head -50
```

### 2. Think Hard о подходе

Ответь на вопросы:
- Какие файлы нужно изменить?
- Какие новые файлы создать?
- Какие зависимости добавить?
- Какие риски есть?
- Как это повлияет на существующий код?
- Какие тесты нужны?

### 3. Document Plan

Запиши план в `.claude-workspace/current-task.md`:

```markdown
## Task: [название]

### Objective
[Чёткая цель в 1-2 предложения]

### Complexity: S/M/L/XL
### Estimated Steps: N
### Risk Level: Low/Medium/High

### Scope
**In Scope:**
- ...

**Out of Scope:**
- ...

### Implementation Steps
1. [ ] **Step 1: [Title]**
   - Files: `path/to/file`
   - Changes: [what to change]
   - Tests: [what to test]
   - Estimated time: X min

2. [ ] **Step 2: [Title]**
   ...

### Files to Create
- `path/to/new.ts` — [purpose]

### Files to Modify
- `path/to/existing.ts` — [what changes]

### Dependencies
- [если нужны новые пакеты]

### Success Criteria
- [ ] All tests pass
- [ ] No linting errors
- [ ] [Specific criterion 1]
- [ ] [Specific criterion 2]

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| ... | ... |
```

### 4. Update Tracking

```bash
# Обнови progress.md
echo "## $(date '+%Y-%m-%d %H:%M') - Planning: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Status: Plan created" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md

# Если новая фича - добавь в features.json
```

## Rules

- Используй **"think hard"** или **"ultrathink"** для сложных задач
- НЕ начинай писать код пока план не одобрен пользователем
- Каждый шаг должен быть выполним за < 30 минут
- Спроси подтверждение перед переходом к `/project:implement`

## Output

После создания плана:
1. Покажи краткое summary
2. Спроси: "План готов. Начинаем имплементацию с `/project:implement`?"