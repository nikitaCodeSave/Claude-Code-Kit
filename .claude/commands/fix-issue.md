---
description: Analyze and fix a GitHub issue by number. Use when user mentions issue number or wants to fix a specific GitHub issue. Follows TDD approach.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---
# Fix GitHub Issue: $ARGUMENTS

> `$ARGUMENTS` — номер issue
> Пример: `/fix-issue 123` → $ARGUMENTS = "123"

Проанализируй и исправь GitHub issue #$ARGUMENTS.

## Context Discovery

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

## Pre-Requisites

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

## Process

### 1. Get Issue Details

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

### 2. Investigate the Problem

```bash
# Поиск в codebase по ключевым словам из issue
# [extract keywords from title/body and search]

# Проверь связанные PRs
gh pr list --search "issue:$ARGUMENTS"

# Проверь git history связанных файлов
# [after identifying files]
```

### 3. Reproduce Locally (если возможно)

```bash
# Запусти dev server
npm run dev &
sleep 5

# Попробуй воспроизвести проблему
# [based on issue description]

# Если есть error message - найди в коде
rg "error message from issue" --type-add 'code:*.{ts,js,py}' -t code
```

### 4. Plan the Fix

Используй **"think hard"** чтобы понять:
- Почему проблема возникает?
- Где именно в коде ошибка?
- Какие побочные эффекты может иметь исправление?
- Нужны ли миграции или breaking changes?

Запиши план в `.claude-workspace/current-task.md`:

```markdown
## Fix: Issue #$ARGUMENTS - [Title]

### Problem Analysis
[Описание проблемы и root cause]

### Solution Approach
[Описание решения]

### Files to Change
- `path/to/file.ts` — [what to change]

### Test Strategy
- [ ] Add test reproducing the bug
- [ ] Verify fix doesn't break existing tests

### Risks
- [Potential side effects]
```

### 5. Implement Fix (TDD)

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

### 6. Verify

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

### 7. Commit and PR

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

### 8. Update Tracking

```bash
# Обнови progress.md
echo "## $(date '+%Y-%m-%d %H:%M') - Fixed Issue #$ARGUMENTS" >> .claude-workspace/progress.md
echo "- Issue: $ISSUE_TITLE" >> .claude-workspace/progress.md
echo "- PR: [link]" >> .claude-workspace/progress.md
echo "- Status: Ready for review" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md
```

## Output Format

```markdown
## Issue #$ARGUMENTS Fixed

### Issue
**Title:** [title]
**Labels:** [labels]

### Root Cause
[1-2 sentences explaining why the bug occurred]

### Solution
[1-2 sentences explaining the fix]

### Changes Made
| File | Change |
|------|--------|
| `path/file.ts` | [description] |
| `path/test.ts` | Added regression test |

### Tests
- New test: `test_issue_$ARGUMENTS_regression`
- All existing tests pass
- Coverage: X% (no decrease)

### PR
**Branch:** `fix/issue-$ARGUMENTS`
**PR:** [link to PR]

### Verification
- [x] Bug no longer reproduces
- [x] All tests pass
- [x] No regressions
- [x] Linting/types OK

### Next Steps
- [ ] Wait for PR review
- [ ] Address review comments if any
- [ ] Merge after approval
```

## Error Handling

### Issue Not Found
```markdown
Issue #$ARGUMENTS not found

Possible reasons:
- Issue number is incorrect
- Issue is in a different repository
- You don't have access to this issue

Run `gh issue list` to see available issues.
```

### Cannot Reproduce
```markdown
Cannot reproduce issue #$ARGUMENTS locally

**What I tried:**
- [Steps attempted]

**Possible reasons:**
- Environment-specific issue
- Missing data/configuration
- Already fixed in current code

**Recommendations:**
1. Ask for more details in the issue
2. Check if issue is still relevant
3. Try on different environment
```

## Extended Error Handling

| Ситуация | Действие |
|----------|----------|
| gh not installed | Предложить `brew install gh` или ручной workaround |
| gh not authenticated | Запустить `gh auth login` |
| Issue closed | Проверить PR, сообщить пользователю |
| Issue already assigned | Спросить продолжать ли |
| No permissions to repo | Предложить fork |
| Cannot reproduce | Запросить больше информации |

## Keyword Extraction Examples

```bash
# Из title: "Login fails with special characters"
rg "login|Login" --type py -C 3
rg "special.*character|character.*special" --type py -C 2

# Из labels: "bug", "authentication"
rg "auth|authenticate" --type py -l
```

## Constraints

### ЗАПРЕЩЕНО
- Push без тестов
- PR без описания
- Закрывать issue без PR
- Рефакторинг "заодно"

### ОБЯЗАТЕЛЬНО
- Упомянуть issue в commit: `fix: ... (closes #123)`
- Тест воспроизводящий баг ПЕРЕД fix
- Минимальные изменения
