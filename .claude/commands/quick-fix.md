---
description: Быстрое исправление бага без полного цикла планирования. Только для мелких очевидных фиксов < 20 строк. НЕ для новых фич или рефакторинга.
allowed-tools: Read, Edit, Bash, Grep, Glob
---
# Quick Fix: $ARGUMENTS

> `$ARGUMENTS` — описание бага после команды
> Пример: `/quick-fix login fails with spaces` → $ARGUMENTS = "login fails with spaces"

Быстрое исправление небольшого бага БЕЗ полного цикла планирования.

## Context Discovery

При вызове СНАЧАЛА:

```bash
# 1. Текущая задача (если есть)
cat .claude-workspace/current-task.md 2>/dev/null | head -10

# 2. Недавние изменения (возможная причина бага)
git diff --stat HEAD~3 2>/dev/null | head -10

# 3. Tech stack
cat pyproject.toml 2>/dev/null | head -10 || cat package.json 2>/dev/null | head -10
```

## Quick Fix Criteria

| Критерий | Quick Fix | Нужен /plan |
|----------|-----------|-------------|
| Строк кода | < 20 | > 20 |
| Файлов | 1-2 | > 2 |
| Тестов новых | 1 | > 3 |
| Зависимости | 0 новых | Любые новые |
| API контракт | Без изменений | Меняется |

Если сложнее → используй `/plan`

## Constraints

### ЗАПРЕЩЕНО
- Рефакторинг "заодно"
- Изменение API контракта
- Добавление новых зависимостей
- Коммит без теста на баг

### ОБЯЗАТЕЛЬНО
- Один тест воспроизводящий баг
- Минимальные изменения
- Коммит сразу после фикса

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

```python
# Напиши тест воспроизводящий баг в tests/test_*.py
def test_bug_description():
    """Тест ДОЛЖЕН УПАСТЬ до фикса."""
    result = function_with_bug(problematic_input)
    assert result == expected_value
```

```bash
# Запусти тест (должен FAIL)
pytest tests/test_module.py::test_bug_description -v
```

### 4. Fix Minimally

- Внеси минимальные изменения
- Только то что нужно для fix
- НЕ рефактори "заодно"

### 5. Verify

```bash
# Тест теперь проходит
pytest tests/test_module.py::test_bug_description -v
# Должен быть PASS

# Все остальные тесты тоже
pytest tests/ -v

# Linting OK
ruff check src/
# или
ruff check . --fix
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
## Quick Fix Complete: $ARGUMENTS

### Problem
[Что было сломано — 1-2 предложения]

### Solution
[Что исправили — 1-2 предложения]

### Changes
- `src/module.py:42` — [description]

### Test Added
- `tests/test_module.py::test_bug_description` — ensures bug doesn't regress

### Commit
`abc1234` fix(scope): $ARGUMENTS
```

## If Fix is Not Quick

Если в процессе понял что fix сложнее:

```markdown
⚠️ This fix is more complex than expected.

**Reason:** [почему]

**Recommendation:** Run `/plan $ARGUMENTS` for proper planning.
```

И останови работу.

## Update Progress

После завершения quick fix добавь запись в `.claude-workspace/progress.md`:

```bash
echo "## $(date '+%Y-%m-%d %H:%M') - Quick Fix: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Bug: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Files changed: [список файлов]" >> .claude-workspace/progress.md
echo "- Commit: [hash]" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md
```