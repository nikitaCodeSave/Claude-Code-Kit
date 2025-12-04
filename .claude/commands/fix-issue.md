# Fix GitHub Issue: $ARGUMENTS

Проанализируй и исправь GitHub issue #$ARGUMENTS.

## Процесс

### 1. Получи детали issue
```bash
gh issue view $ARGUMENTS
```

### 2. Исследуй проблему
- Найди релевантные файлы в codebase
- Воспроизведи проблему локально если возможно
- Изучи git history связанных файлов
- Проверь есть ли связанные issues/PRs

### 3. Определи причину проблемы
Используй "think hard" чтобы понять:
- Почему проблема возникает?
- Где именно в коде ошибка?
- Какие побочные эффекты может иметь исправление?

### 4. Спланируй исправление
Запиши план в `.claude-workspace/current-task.md`:
```markdown
## Исправление бага: Issue #$ARGUMENTS

### Проблема
[Описание проблемы]

### Причина
[Причина проблемы]

### Решение
[Описание решения]

### Файлы для изменения
- ...

### Стратегия тестирования
- ...
```

### 5. Реализуй исправление (TDD)
1. Напиши тест воспроизводящий баг
2. Запусти тест - он должен ПАДАТЬ
3. Исправь код
4. Запусти тест - он должен ПРОХОДИТЬ
5. Запусти ВСЕ тесты - ничего не должно сломаться

### 6. Verify
```bash
# Все тесты проходят
npm run test

# Linting OK
npm run lint

# Проверь manually если возможно
```

### 7. Complete
```bash
# Коммит с ссылкой на issue
git add .
git commit -m "fix(scope): description

Fixes #$ARGUMENTS"

# Push и создай PR
git push origin fix/issue-$ARGUMENTS
gh pr create --title "Fix #$ARGUMENTS: [title]" --body "Closes #$ARGUMENTS"
```

### 8. Update Tracking
- Обнови progress.md
- Добавь запись о fix

## Output
```markdown
## Issue #$ARGUMENTS Fixed

### Summary
[Что было исправлено]

### Changes Made
- `file1.py`: [description]
- `file2.py`: [description]

### Tests Added
- `test_file.py::test_name`: [what it tests]

### PR
[Link to PR]

### Verification
- [ ] Bug no longer reproduces
- [ ] All tests pass
- [ ] No regressions
```
