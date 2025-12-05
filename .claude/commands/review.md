---
description: Independent code review of recent changes. Use after implementation completion, before merge. Provides objective quality assessment with fresh perspective.
allowed-tools: Read, Grep, Glob, Bash
---
# Review Recent Changes

Проведи code review недавних изменений как **НЕЗАВИСИМЫЙ** Review Agent.

## Context Discovery

При вызове СНАЧАЛА:

```bash
# 1. Что изменилось
git log --oneline -5 2>/dev/null
git diff --stat HEAD~1 2>/dev/null | tail -5

# 2. Что должно было быть сделано
cat .claude-workspace/current-task.md 2>/dev/null | head -10
```

## Arguments

`$ARGUMENTS`:
- Число — количество коммитов для review (default: auto-detect)
- `all` — все uncommitted + последние 5 коммитов
- `staged` — только staged changes
- `branch` — все коммиты текущей ветки относительно main/master

## Setup

```bash
# 1. Сбрось контекст — ты независимый reviewer
echo "=== Starting Independent Review ==="

# 2. Определи scope review
if [ "$ARGUMENTS" = "staged" ]; then
  DIFF_CMD="git diff --cached"
  SCOPE="staged changes"
elif [ "$ARGUMENTS" = "branch" ]; then
  BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null)
  DIFF_CMD="git diff $BASE..HEAD"
  SCOPE="branch changes since $(git rev-parse --short $BASE)"
elif [ "$ARGUMENTS" = "all" ]; then
  DIFF_CMD="git diff HEAD~5"
  SCOPE="last 5 commits + uncommitted"
elif [ -n "$ARGUMENTS" ] && [ "$ARGUMENTS" -eq "$ARGUMENTS" ] 2>/dev/null; then
  DIFF_CMD="git diff HEAD~$ARGUMENTS"
  SCOPE="last $ARGUMENTS commits"
else
  # Auto-detect: find commits since last review or last 5
  DIFF_CMD="git diff HEAD~5"
  SCOPE="last 5 commits (auto)"
fi

echo "Review scope: $SCOPE"

# 3. Прочитай план (что должно было быть сделано)
cat .claude-workspace/current-task.md 2>/dev/null | head -30
```

## Review Process

### 1. Understand Intent

```bash
# Что должно было быть сделано?
cat .claude-workspace/current-task.md

# Какие коммиты входят в review?
git log --oneline -10
```

### 2. Gather Changes

```bash
# Статистика изменений
git diff HEAD~5 --stat

# Какие файлы затронуты?
git show --stat HEAD~5..HEAD

# Детальный diff
git diff HEAD~5
```

### 3. Run Automated Checks

```bash
# Тесты
npm test 2>&1 | tail -20 || pytest -v 2>&1 | tail -20

# Linting
npm run lint 2>&1 | head -30 || ruff check . 2>&1 | head -30

# Type checking
npm run typecheck 2>&1 | head -20 || mypy . 2>&1 | head -20
```

### 4. Security Scan

```bash
# Secrets detection
rg -i "(api[_-]?key|password|secret|token|credential).*[=:].*['\"][^'\"]{8,}" --type-add 'code:*.{ts,js,py,go}' -t code | head -10

# Hardcoded values
rg "(localhost|127\.0\.0\.1|0\.0\.0\.0):[0-9]+" --type-add 'code:*.{ts,js,py}' -t code | head -10

# Console/print statements
rg "(console\.(log|debug|info)|print\()" --type-add 'code:*.{ts,js,py}' -t code | grep -v test | head -10
```

### 5. Deep Review Each File

Для каждого изменённого файла:
- Читай код как будто видишь **впервые**
- Проверяй логику (trace through mentally)
- Ищи edge cases
- Проверяй соответствие code style

## Review Checklist

### Correctness ✓
- [ ] Реализация соответствует requirements из плана
- [ ] Логика корректна (mental trace через код)
- [ ] Edge cases обработаны
- [ ] Error handling присутствует и корректен
- [ ] Нет очевидных race conditions/deadlocks

### Code Quality ✓
- [ ] Читаемый код (понятен без комментариев)
- [ ] Понятные имена переменных и функций
- [ ] Нет дублирования (DRY)
- [ ] Функции не слишком длинные (< 50 lines)
- [ ] Следует code style из CLAUDE.md
- [ ] Consistent formatting

### Testing ✓
- [ ] Тесты существуют для новой функциональности
- [ ] Тесты покрывают happy path
- [ ] Тесты покрывают edge cases
- [ ] Тесты покрывают error cases
- [ ] Тесты независимы друг от друга
- [ ] Тесты не overfitted к реализации

### Security ✓
- [ ] Нет hardcoded secrets/credentials
- [ ] Input validation присутствует
- [ ] Безопасная обработка ошибок (no stack traces to users)
- [ ] Нет SQL/XSS/Command injection vulnerabilities

### Performance ✓
- [ ] Нет O(n²) где можно O(n)
- [ ] Нет N+1 database queries
- [ ] Нет unnecessary computations в loops
- [ ] Нет memory leaks (subscriptions, event listeners)

## Auto-REJECT Criteria

**НЕМЕДЛЕННО отклонить если найдено:**

| Finding | Severity | Action |
|---------|----------|--------|
| Hardcoded secrets | CRITICAL | ❌ REJECT |
| SQL/Command injection | CRITICAL | ❌ REJECT |
| console.log в production | HIGH | ⚠️ CHANGES REQUESTED |
| Missing tests for new code | HIGH | ⚠️ CHANGES REQUESTED |
| Coverage decreased | HIGH | ⚠️ CHANGES REQUESTED |
| Breaking changes без docs | HIGH | ⚠️ CHANGES REQUESTED |

## Output Format

```markdown
## Code Review Summary

**Reviewer:** Review Agent (Independent)
**Date:** [timestamp]
**Scope:** [what was reviewed]
**Commits:** [hash range or description]
**Files Changed:** [count]

---

### Verdict

**Status:** ✅ APPROVED / ⚠️ CHANGES REQUESTED / ❌ REJECTED

**Quality Score:** ⭐⭐⭐⭐☆ (4/5)

---

### Automated Checks

| Check | Status | Details |
|-------|--------|---------|
| Tests | ✅/❌ | X passing, Y failing |
| Linting | ✅/❌ | X errors, Y warnings |
| Types | ✅/❌ | X errors |
| Security | ✅/⚠️/❌ | [findings] |

---

### Findings

#### 🔴 Critical (must fix)
1. **[Title]**
   - **File:** `path/file.ts:42`
   - **Issue:** [what's wrong]
   - **Risk:** [what could happen]
   - **Fix:** [how to fix]

#### 🟠 High Priority (should fix)
1. ...

#### 🟡 Medium (recommended)
1. ...

#### 🔵 Low / Suggestions
1. ...

---

### What's Good ✅
- [Positive aspect 1]
- [Positive aspect 2]
- [Positive aspect 3]

---

### Before Merge Checklist

- [ ] All critical findings addressed
- [ ] All high priority findings addressed
- [ ] Tests pass
- [ ] Coverage maintained or improved
- [ ] Documentation updated (if needed)

---

### Recommended Actions

1. **[Priority 1]** — [specific action]
2. **[Priority 2]** — [specific action]

💡 After fixes, run `/project:review staged` to re-review
```

## Example Output

```markdown
## Code Review: feat(auth): add JWT validation

**Scope:** 3 files, +127/-23 lines
**Verdict:** ✅ APPROVED with suggestions

### MEDIUM — Consider caching
- File: src/auth/jwt.py:45
- Issue: Token validation on every request
- Fix: Add Redis cache for validated tokens

### What's Good
- Clear separation of concerns
- Comprehensive tests (92% coverage)
- Good error messages
```

## Quality Checklist

Перед завершением проверь:

- [ ] Все automated checks запущены
- [ ] Критические проблемы описаны с примерами кода
- [ ] Позитивные аспекты упомянуты
- [ ] Конкретные actions предложены
- [ ] Verdict соответствует findings

## Rules

- Будь **объективен** — хвали хорошее, указывай на плохое
- Объясняй **ПОЧЕМУ** что-то плохо, не просто "это плохо"
- Предлагай **конкретные решения**
- **Приоритизируй** — не придирайся к мелочам если есть серьёзные проблемы
- Если code отличный — так и скажи!