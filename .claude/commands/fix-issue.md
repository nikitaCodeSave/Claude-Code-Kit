---
description: Анализ и исправление GitHub issue по номеру. Использовать при упоминании номера issue или запросе исправить конкретный issue. Следует TDD подходу.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---
# Исправление GitHub Issue: $ARGUMENTS

> `$ARGUMENTS` — номер issue
> Пример: `/fix-issue 123` → $ARGUMENTS = "123"

Проанализируй и исправь GitHub issue #$ARGUMENTS.

## Сбор контекста

При вызове СНАЧАЛА:

```bash
# 1. Проверь gh CLI
gh auth status 2>/dev/null || echo "WARNING: gh not authenticated"

# 2. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null | head -10

# 3. Git status
git status --short 2>/dev/null

# 4. Текущая ветка
git branch --show-current 2>/dev/null
```

## Предварительные требования

```bash
# 1. Проверь что gh CLI установлен и авторизован
if ! command -v gh &> /dev/null; then
  echo "ERROR: GitHub CLI (gh) not installed"
  echo "Install: https://cli.github.com/"
  exit 1
fi

# 2. Проверь авторизацию
if ! gh auth status &> /dev/null; then
  echo "ERROR: Not authenticated with GitHub"
  echo "Run: gh auth login"
  exit 1
fi

# 3. Валидируй номер issue
if ! [[ "$ARGUMENTS" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Invalid issue number: $ARGUMENTS"
  echo "Usage: /project:fix-issue 123"
  exit 1
fi
```

## Процесс

### 1. Получить детали Issue

```bash
# Получи детали issue
gh issue view $ARGUMENTS

# Сохрани в переменные для reference
ISSUE_TITLE=$(gh issue view $ARGUMENTS --json title -q '.title')
ISSUE_BODY=$(gh issue view $ARGUMENTS --json body -q '.body')
ISSUE_LABELS=$(gh issue view $ARGUMENTS --json labels -q '.labels[].name' | tr '\n' ', ')

echo "=== Issue #$ARGUMENTS ==="
echo "Title: $ISSUE_TITLE"
echo "Labels: $ISSUE_LABELS"
```

### 2. Исследовать проблему

```bash
# Поиск в codebase по ключевым словам из issue
# [extract keywords from title/body and search]

# Проверь связанные PRs
gh pr list --search "issue:$ARGUMENTS"

# Проверь git history связанных файлов
# [after identifying files]
```

### 3. Воспроизвести локально (если возможно)

```bash
# Запусти dev server
npm run dev &
sleep 5

# Попробуй воспроизвести проблему
# [based on issue description]

# Если есть error message - найди в коде
rg "error message from issue" --type-add 'code:*.{ts,js,py}' -t code
```

### 4. Спланировать исправление

Используй **"think hard"** чтобы понять:
- Почему проблема возникает?
- Где именно в коде ошибка?
- Какие побочные эффекты может иметь исправление?
- Нужны ли миграции или breaking changes?

Запиши план в `.claude-workspace/current-task.md`:

```markdown
## Исправление: Issue #$ARGUMENTS - [Заголовок]

### Анализ проблемы
[Описание проблемы и root cause]

### Подход к решению
[Описание решения]

### Файлы для изменения
- `path/to/file.ts` — [что изменить]

### Стратегия тестирования
- [ ] Добавить тест воспроизводящий баг
- [ ] Проверить что фикс не ломает существующие тесты

### Риски
- [Потенциальные побочные эффекты]
```

### 5. Реализовать исправление (TDD)

```bash
# 1. Создай ветку
git checkout -b fix/issue-$ARGUMENTS

# 2. Напиши тест воспроизводящий баг
# [create test file or add test case]
```

```python
# tests/test_issue_123.py
def test_issue_123_regression():
    """Тест воспроизводящий баг из issue #123."""
    result = problematic_function(edge_case_input)
    assert result == expected_output
```

```bash
# 3. Запусти тест - ДОЛЖЕН УПАСТЬ
pytest tests/test_issue_$ARGUMENTS.py -v

# 4. Исправь код
# [make minimal changes to fix]

# 5. Запусти тест - ДОЛЖЕН ПРОЙТИ
pytest tests/test_issue_$ARGUMENTS.py -v

# 6. Запусти ВСЕ тесты
pytest tests/ -v
```

### 6. Проверить

```bash
# Все тесты проходят
pytest tests/ -v

# Linting OK
ruff check src/

# Type checking OK
mypy src/ 2>/dev/null || echo "mypy not configured"

# Если UI issue - проверь визуально
# [manual verification if needed]
```

### 7. Коммит и PR

```bash
# Коммит с ссылкой на issue
git add .
git commit -m "fix(scope): [description]

Fixes #$ARGUMENTS

- [Change 1]
- [Change 2]
- Added test for regression"

# Push ветку
git push origin fix/issue-$ARGUMENTS

# Создай PR
gh pr create \
  --title "Fix #$ARGUMENTS: [title]" \
  --body "## Summary
Fixes #$ARGUMENTS

## Changes
- [List of changes]

## Testing
- [x] Added test reproducing the issue
- [x] All tests pass
- [x] Manual verification (if applicable)

## Screenshots
[If UI change]
" \
  --assignee @me
```

### 8. Обновить отслеживание

```bash
# Обнови progress.md
echo "## $(date '+%Y-%m-%d %H:%M') - Fixed Issue #$ARGUMENTS" >> .claude-workspace/progress.md
echo "- Issue: $ISSUE_TITLE" >> .claude-workspace/progress.md
echo "- PR: [link]" >> .claude-workspace/progress.md
echo "- Status: Ready for review" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md
```

### 9. Документировать решения (для сложных фиксов)

Если при исправлении issue было принято архитектурное решение
(выбор подхода, изменение структуры, workaround), добавь в `.claude-workspace/decisions.md`:

```markdown
## ADR-NNN: Исправление Issue #$ARGUMENTS

**Дата:** $(date '+%Y-%m-%d')
**Статус:** Принято
**Контекст:** GitHub Issue #$ARGUMENTS - [краткое описание]

### Проблема
[Описание проблемы из issue]

### Выбранное решение
[Выбранный подход к исправлению]

### Рассмотренные альтернативы
- [Другой подход] — [почему отклонён]

### Компромиссы
- [Компромиссы принятого решения]
```

## Формат вывода

```markdown
## Issue #$ARGUMENTS исправлен

### Issue
**Заголовок:** [заголовок]
**Метки:** [метки]

### Корневая причина
[1-2 предложения объясняющих почему возник баг]

### Решение
[1-2 предложения объясняющих исправление]

### Внесённые изменения
| Файл | Изменение |
|------|-----------|
| `path/file.ts` | [описание] |
| `path/test.ts` | Добавлен тест на регрессию |

### Тесты
- Новый тест: `test_issue_$ARGUMENTS_regression`
- Все существующие тесты проходят
- Покрытие: X% (без снижения)

### PR
**Ветка:** `fix/issue-$ARGUMENTS`
**PR:** [ссылка на PR]

### Верификация
- [x] Баг больше не воспроизводится
- [x] Все тесты проходят
- [x] Нет регрессий
- [x] Линтинг/типы OK

### Следующие шаги
- [ ] Дождаться ревью PR
- [ ] Исправить замечания ревьюера (если будут)
- [ ] Смержить после одобрения
```

## Обработка ошибок

### Issue не найден
```markdown
Issue #$ARGUMENTS не найден

Возможные причины:
- Номер issue неверен
- Issue в другом репозитории
- Нет доступа к этому issue

Запусти `gh issue list` чтобы увидеть доступные issues.
```

### Не удаётся воспроизвести
```markdown
Не удаётся воспроизвести issue #$ARGUMENTS локально

**Что пробовал:**
- [Предпринятые шаги]

**Возможные причины:**
- Проблема специфична для окружения
- Недостающие данные/конфигурация
- Уже исправлено в текущем коде

**Рекомендации:**
1. Запросить больше деталей в issue
2. Проверить актуальность issue
3. Попробовать в другом окружении
```

## Расширенная обработка ошибок

| Ситуация | Действие |
|----------|----------|
| gh not installed | Предложить `brew install gh` или ручной workaround |
| gh not authenticated | Запустить `gh auth login` |
| Issue closed | Проверить PR, сообщить пользователю |
| Issue already assigned | Спросить продолжать ли |
| No permissions to repo | Предложить fork |
| Cannot reproduce | Запросить больше информации |

## Примеры извлечения ключевых слов

```bash
# Из title: "Login fails with special characters"
rg "login|Login" --type py -C 3
rg "special.*character|character.*special" --type py -C 2

# Из labels: "bug", "authentication"
rg "auth|authenticate" --type py -l
```

## Ограничения

### ЗАПРЕЩЕНО
- Push без тестов
- PR без описания
- Закрывать issue без PR
- Рефакторинг "заодно"

### ОБЯЗАТЕЛЬНО
- Упомянуть issue в commit: `fix: ... (closes #123)`
- Тест воспроизводящий баг ПЕРЕД fix
- Минимальные изменения
