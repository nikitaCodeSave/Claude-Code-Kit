---
description: Quick bug fix without full planning cycle. Use for small, obvious fixes < 20 lines of code. NOT for new features or refactoring.
allowed-tools: Read, Edit, Bash, Grep, Glob
---
# Quick Fix: $ARGUMENTS

Быстрое исправление небольшого бага БЕЗ полного цикла планирования.

## Constraints

⚠️ Используй ТОЛЬКО если:
- Изменения < 20 строк кода
- Очевидный баг с понятным fix
- НЕ новая функциональность
- НЕ рефакторинг

Если сложнее → используй `/project:plan`

## Process

### 1. Find the Problem

```bash
# Поиск по описанию бага
rg "$ARGUMENTS" --type-add 'code:*.{ts,js,py,go}' -t code -C 2 | head -30

# Или по error message
rg "error|Error|ERROR" --type-add 'code:*.{ts,js,py}' -t code | grep -i "$ARGUMENTS" | head -10
```

### 2. Read and Understand

```bash
# Прочитай файл с проблемой
# [use Read tool on identified file]
```

### 3. Write Test First

```bash
# Напиши тест воспроизводящий баг
# Тест ДОЛЖЕН УПАСТЬ

# Запусти тест
npm test -- --grep "test for bug"
# Должен быть FAIL
```

### 4. Fix Minimally

- Внеси минимальные изменения
- Только то что нужно для fix
- НЕ рефактори "заодно"

### 5. Verify

```bash
# Тест теперь проходит
npm test -- --grep "test for bug"
# Должен быть PASS

# Все остальные тесты тоже
npm test

# Linting OK
npm run lint
```

### 6. Commit

```bash
git add .
git commit -m "fix($SCOPE): $ARGUMENTS

- [краткое описание что исправлено]
- Added test for regression"
```

## Output Format

```markdown
## ✅ Quick Fix Complete: $ARGUMENTS

### Problem
[Что было сломано — 1-2 предложения]

### Solution
[Что исправили — 1-2 предложения]

### Changes
- `path/to/file.ts:42` — [description]

### Test Added
- `test_file.ts::test_name` — ensures bug doesn't regress

### Commit
`abc1234` fix(scope): $ARGUMENTS
```

## If Fix is Not Quick

Если в процессе понял что fix сложнее:

```markdown
⚠️ This fix is more complex than expected.

**Reason:** [почему]

**Recommendation:** Run `/project:plan $ARGUMENTS` for proper planning.
```

И останови работу.