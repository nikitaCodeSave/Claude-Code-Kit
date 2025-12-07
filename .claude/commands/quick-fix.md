---
description: Быстрое исправление бага без полного цикла планирования. Только для мелких очевидных фиксов < 20 строк. НЕ для новых фич или рефакторинга.
allowed-tools: Read, Edit, Bash, Grep, Glob, Task
---
# Быстрое исправление: $ARGUMENTS

## Интеграция с агентами

**ОПЦИОНАЛЬНО** использовать Task tool для делегирования code-agent в упрощённом режиме:

```
[Task: code-agent]
prompt: |
  ## Задача: Quick Fix "$ARGUMENTS"

  ### Режим
  УПРОЩЁННЫЙ — без полного TDD цикла

  ### Ограничения
  - Максимум 20 строк изменений
  - Максимум 2 файла
  - 1 тест на регрессию
  - Без новых зависимостей
  - Без изменения API

  ### Процесс
  1. Найди проблему
  2. Напиши тест воспроизводящий баг (MUST FAIL)
  3. Минимальное исправление
  4. Тест проходит
  5. Все тесты проходят
  6. Коммит

  ### Если сложнее
  Остановись и предложи /create-plan
```

> `$ARGUMENTS` — описание бага после команды
> Пример: `/quick-fix login fails with spaces` → $ARGUMENTS = "login fails with spaces"

Быстрое исправление небольшого бага БЕЗ полного цикла планирования.

## Сбор контекста

При вызове СНАЧАЛА:

```bash
# 1. Текущая задача (если есть)
cat .claude-workspace/current-task.md 2>/dev/null | head -10

# 2. Недавние изменения (возможная причина бага)
git diff --stat HEAD~3 2>/dev/null | head -10

# 3. Tech stack
cat pyproject.toml 2>/dev/null | head -10 || cat package.json 2>/dev/null | head -10
```

## Критерии быстрого исправления

| Критерий | Quick Fix | Нужен /create-plan |
|----------|-----------|-------------|
| Строк кода | < 20 | > 20 |
| Файлов | 1-2 | > 2 |
| Тестов новых | 1 | > 3 |
| Зависимости | 0 новых | Любые новые |
| API контракт | Без изменений | Меняется |

Если сложнее → используй `/create-plan`

## Ограничения

### ЗАПРЕЩЕНО
- Рефакторинг "заодно"
- Изменение API контракта
- Добавление новых зависимостей
- Коммит без теста на баг

### ОБЯЗАТЕЛЬНО
- Один тест воспроизводящий баг
- Минимальные изменения
- Коммит сразу после фикса

## Процесс

### 1. Найти проблему

```bash
# Поиск по описанию бага
rg "$ARGUMENTS" --type-add 'code:*.{ts,js,py,go}' -t code -C 2 | head -30

# Или по error message
rg "error|Error|ERROR" --type-add 'code:*.{ts,js,py}' -t code | grep -i "$ARGUMENTS" | head -10
```

### 2. Прочитать и понять

```bash
# Прочитай файл с проблемой
# [use Read tool on identified file]
```

### 3. Сначала написать тест

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

### 4. Минимальное исправление

- Внеси минимальные изменения
- Только то что нужно для fix
- НЕ рефактори "заодно"

### 5. Проверить

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

### 6. Закоммитить

```bash
git add .
git commit -m "fix($SCOPE): $ARGUMENTS

- [краткое описание что исправлено]
- Added test for regression"
```

## Формат вывода

```markdown
## Быстрое исправление завершено: $ARGUMENTS

### Проблема
[Что было сломано — 1-2 предложения]

### Решение
[Что исправили — 1-2 предложения]

### Изменения
- `src/module.py:42` — [описание]

### Добавленный тест
- `tests/test_module.py::test_bug_description` — защита от регрессии бага

### Коммит
`abc1234` fix(scope): $ARGUMENTS
```

## Если исправление не быстрое

Если в процессе понял что fix сложнее:

```markdown
⚠️ Это исправление сложнее чем ожидалось.

**Причина:** [почему]

**Рекомендация:** Запусти `/create-plan $ARGUMENTS` для полноценного планирования.
```

И останови работу.

## Обновление прогресса

После завершения quick fix добавь запись в `.claude-workspace/progress.md`:

```bash
echo "## $(date '+%Y-%m-%d %H:%M') - Quick Fix: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Bug: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Files changed: [список файлов]" >> .claude-workspace/progress.md
echo "- Commit: [hash]" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md
```