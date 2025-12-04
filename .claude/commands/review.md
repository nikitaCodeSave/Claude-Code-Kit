# Review Recent Changes

Проведи code review недавних изменений как НЕЗАВИСИМЫЙ Review Agent.

## Arguments
$ARGUMENTS = количество коммитов для review (default: 5)

## Process

### 1. Сбрось контекст
Забудь о предыдущей работе. Ты - независимый reviewer.

### 2. Изучи план
```bash
cat .claude-workspace/current-task.md
```

### 3. Изучи изменения
```bash
git diff HEAD~$ARGUMENTS
git log --oneline -$ARGUMENTS
git show --stat HEAD~$ARGUMENTS..HEAD
```

### 4. Review каждого файла

## Review Checklist

### Correctness
- [ ] Реализация соответствует requirements из плана
- [ ] Edge cases обработаны
- [ ] Ошибки handled gracefully
- [ ] Нет race conditions или deadlocks

### Code Quality
- [ ] Следует code style из CLAUDE.md
- [ ] Нет code duplication (DRY)
- [ ] Понятные имена переменных и функций
- [ ] Функции не слишком длинные (<50 lines)
- [ ] Достаточная документация/комментарии

### Testing
- [ ] Тесты существуют для новой функциональности
- [ ] Тесты покрывают happy path
- [ ] Тесты покрывают edge cases
- [ ] Тесты покрывают error cases
- [ ] Тесты не overfitted к реализации

### Security
- [ ] No hardcoded secrets/credentials
- [ ] Input validation присутствует
- [ ] Proper error handling (no stack traces to users)
- [ ] No SQL injection / XSS vulnerabilities

### Performance
- [ ] Нет очевидных N+1 queries
- [ ] Нет unnecessary computations в loops
- [ ] Appropriate caching если нужно

## Output Format

```markdown
## Code Review Summary

**Status:** ✅ Approved / ⚠️ Changes Requested / ❌ Needs Rework

**Reviewed Commits:** [list]

### Findings

#### Critical Issues
1. [CRITICAL] Description
   - File: `path/to/file.py:line`
   - Issue: what's wrong
   - Suggestion: how to fix

#### Major Issues
1. [MAJOR] Description
   - ...

#### Minor Issues / Suggestions
1. [MINOR] Description
   - ...

### What's Good
- [Positive aspects of the code]

### Recommendations
- [Suggestions for improvement]

### Next Steps
- [What should happen next]
```
