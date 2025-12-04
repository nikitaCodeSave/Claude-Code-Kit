---
description: Implements current task from .claude-workspace/current-task.md using strict TDD. Use after plan is approved and ready for coding.
allowed-tools: Read, Edit, MultiEdit, Write, Bash, Grep, Glob
---
# Implement Current Task

Реализуй задачу из `.claude-workspace/current-task.md` следуя TDD.

## Pre-Implementation Checklist

```bash
# 1. Проверь что план существует
if [ ! -f .claude-workspace/current-task.md ]; then
  echo "ERROR: No plan found. Run /project:plan first."
  exit 1
fi

# 2. Покажи текущую задачу
cat .claude-workspace/current-task.md

# 3. Проверь прогресс
cat .claude-workspace/progress.md | tail -20

# 4. Проверь git status
git status --short

# 5. Убедись что тесты проходят (baseline)
npm test 2>&1 | tail -10 || pytest -v 2>&1 | tail -10
```

## Implementation Process

### Для КАЖДОГО шага из плана:

#### 1. Write Test FIRST (RED)
```bash
# Создай тест описывающий expected behavior
# Запусти - он ДОЛЖЕН УПАСТЬ
npm test -- --grep "test name"
```

#### 2. Write Minimal Code (GREEN)
```bash
# Напиши минимум кода для прохождения теста
# Запусти - ДОЛЖЕН ПРОЙТИ
npm test
```

#### 3. Refactor (если нужно)
```bash
# Улучши код без изменения поведения
# Тесты ВСЁ ЕЩЁ должны проходить
npm test
```

#### 4. Commit
```bash
git add .
git commit -m "type(scope): description

Step X/Y of [task-id]"
```

#### 5. Update Tracking
- Отметь `[x]` выполненный шаг в `current-task.md`
- Добавь запись в `progress.md`

## After All Steps Completed

```bash
# 1. Все тесты
npm test

# 2. Linting
npm run lint

# 3. Type checking (если TypeScript)
npm run typecheck

# 4. Build (если есть)
npm run build 2>&1 | tail -20
```

## Completion Checklist

- [ ] Все шаги плана выполнены
- [ ] Все тесты проходят
- [ ] Linting без ошибок
- [ ] Нет `console.log` в production коде
- [ ] `progress.md` обновлён
- [ ] `current-task.md` все шаги отмечены
- [ ] Код закоммичен

## Rules

- Работай над **ОДНИМ** шагом за раз
- **НЕ** пропускай написание тестов
- Коммить **ЧАСТО** (после каждого логического изменения)
- Если что-то сломалось — почини **СРАЗУ**
- **НИКОГДА** не оставляй код в нерабочем состоянии
- Если застрял > 15 минут — запиши в progress.md и спроси помощи

## Output

После завершения покажи:
```markdown
## Implementation Complete

### Files Changed
- `file1.ts` — [description]
- `file2.ts` — [description]

### Tests Added
- `test_file.ts` — [what it tests]

### Git Log
[последние N коммитов]

### Next Steps
- [ ] Run /project:review for code review
- [ ] Or continue with next task
```