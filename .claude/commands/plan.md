---
description: Creates detailed implementation plan for a feature or task. Use when user mentions "plan", "design", "architect", or before implementing any feature > 50 lines of code.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---
# Plan Feature/Task: $ARGUMENTS

> `$ARGUMENTS` — описание задачи после команды
> Пример: `/plan user authentication` → $ARGUMENTS = "user authentication"

Создай детальный план для задачи. **НЕ ПИШИ КОД.**

## Context Discovery

При вызове СНАЧАЛА:

```bash
# 1. Текущий прогресс
cat .claude-workspace/progress.md 2>/dev/null | tail -20

# 2. Есть ли уже план?
cat .claude-workspace/current-task.md 2>/dev/null | head -15

# 3. Недавние коммиты (контекст)
git log --oneline -5 2>/dev/null
```

## Task Size Matrix

| Размер | Строк кода | Шагов | Подход |
|--------|------------|-------|--------|
| S | < 50 | 1-3 | Простой план |
| M | 50-200 | 4-6 | Детальный план |
| L | 200-500 | 7-10 | Декомпозиция на подзадачи |
| XL | > 500 | 10+ | Несколько /plan сессий |

## Process

### 1. Explore (используй explore-agent для сложных задач)

```bash
# Изучи структуру проекта
tree -L 2 -I 'node_modules|__pycache__|.git|.venv|venv' | head -40

# Python: найти сервисы/классы
rg "class.*Service|class.*Handler|class.*Manager" --type py -l | head -10

# Python: найти эндпоинты FastAPI/Flask
rg "@(app|router)\.(get|post|put|delete|patch)" --type py -C 2 | head -30

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
- `src/services/new_service.py` — [purpose]
- `tests/test_new_service.py` — [tests]

### Files to Modify
- `src/main.py` — [what changes]

### Dependencies
- [если нужны новые пакеты в pyproject.toml]

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

## Constraints

### ЗАПРЕЩЕНО
- Писать код в плане (только описания)
- Начинать реализацию без approval пользователя
- Шаги длиннее 30 минут
- Пропускать тесты в плане

### ОБЯЗАТЕЛЬНО
- Указать риски для каждого шага M/L/XL
- Включить тесты в каждый шаг
- Использовать "think hard" или "ultrathink" для сложных задач

## Approval Process

После создания плана:

1. Покажи краткое summary (5-7 пунктов):
   - Цель
   - Размер (S/M/L/XL)
   - Количество шагов
   - Ключевые файлы
   - Основные риски

2. Спроси явно:
   > "План готов. Продолжить с `/implement`?"

3. Дождись явного подтверждения ("да", "proceed", "начинай")

## Output

После создания плана:
1. Покажи краткое summary
2. Спроси: "План готов. Начинаем имплементацию с `/implement`?"