# Plan Feature/Task: $ARGUMENTS

Создай детальный план для задачи. НЕ ПИШИ КОД.

## Process

### 1. Explore (используй subagents для сложных задач)
- Изучи релевантные файлы проекта
- Проверь существующие паттерны в codebase
- Найди похожие реализации

### 2. Think Hard о подходе
Ответь на вопросы:
- Какие файлы нужно изменить?
- Какие новые файлы создать?
- Какие зависимости добавить?
- Какие риски есть?
- Как это повлияет на существующий код?

### 3. Document Plan
Запиши план в `.claude-workspace/current-task.md` в формате:

```markdown
## Task: [название]

### Objective
[Чёткая цель в 1-2 предложения]

### Scope
**In Scope:**
- ...

**Out of Scope:**
- ...

### Implementation Steps
1. [ ] Step 1 - description
2. [ ] Step 2 - description
...

### Files to Modify
- `path/to/file.py` - reason

### Files to Create  
- `path/to/new.py` - purpose

### Dependencies
- [если нужны новые пакеты]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Risks
- Risk 1 - mitigation
```

### 4. Update Tracking
- Обнови `.claude-workspace/progress.md`
- Если новая фича - добавь в `features.json` со статусом "planned"

## Rules
- Используй "think hard" или "ultrathink" для сложных задач
- НЕ начинай писать код пока план не одобрен
- Спроси подтверждение перед переходом к реализации
