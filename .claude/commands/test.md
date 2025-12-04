---
description: End-to-end testing of a feature. Use after implementation to verify feature works as real user would expect. Supports both automated and manual testing flows.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
# Test Feature: $ARGUMENTS

Протестируй фичу "$ARGUMENTS" end-to-end как реальный пользователь.

## Pre-Test Setup

```bash
# 1. Проверь что dev server можно запустить
if [ -f "package.json" ]; then
  echo "Starting dev server..."
  npm run dev &
  DEV_PID=$!
  sleep 5
  
  # Health check
  curl -s http://localhost:3000/health || curl -s http://localhost:3000 | head -5
fi

# 2. Определи test framework
cat package.json 2>/dev/null | jq '.scripts.test, .devDependencies | keys | map(select(contains("jest") or contains("vitest") or contains("playwright")))'

# 3. Найди существующие тесты для фичи
find . -name "*.test.*" -o -name "*.spec.*" | xargs grep -l "$ARGUMENTS" 2>/dev/null | head -10
```

## Testing Process

### 1. Unit/Integration Tests

```bash
# Запусти тесты для конкретной фичи
npm test -- --grep "$ARGUMENTS" --coverage
# или
pytest -k "$ARGUMENTS" -v --cov

# Если нет специфичных тестов, запусти все
npm test
```

### 2. E2E Testing

#### С Browser Automation (Playwright/Puppeteer MCP)

```bash
# Запусти Playwright тесты
npx playwright test --grep "$ARGUMENTS"

# Или manual flow через MCP:
# 1. Открой http://localhost:3000
# 2. Навигируй к фиче
# 3. Выполни user actions
# 4. Сделай скриншоты ключевых точек
# 5. Проверь результаты визуально
```

#### Без Browser Automation (API Testing)

```bash
# Health check
curl -s -w "\nStatus: %{http_code}\n" http://localhost:3000/health

# GET endpoints
curl -s http://localhost:3000/api/[endpoint] | jq

# POST endpoints
curl -s -X POST http://localhost:3000/api/[endpoint] \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' | jq

# Check error handling
curl -s -w "\nStatus: %{http_code}\n" http://localhost:3000/api/notfound
```

### 3. Test Scenarios Matrix

Для фичи "$ARGUMENTS" проверь:

| # | Scenario | Input | Expected | Status |
|---|----------|-------|----------|--------|
| 1 | Happy Path | valid data | success | ⬜ |
| 2 | Empty Input | `""`, `null` | validation error | ⬜ |
| 3 | Invalid Input | wrong type/format | type error | ⬜ |
| 4 | Boundary Min | minimum valid | success/error | ⬜ |
| 5 | Boundary Max | maximum valid | success/error | ⬜ |
| 6 | Special Chars | `<script>`, `'; DROP` | sanitized | ⬜ |
| 7 | Concurrent | parallel requests | no race condition | ⬜ |
| 8 | Network Error | timeout/500 | graceful handling | ⬜ |

### 4. Coverage Check

```bash
# Проверь coverage после тестов
npm test -- --coverage
# или
pytest --cov --cov-report=term-missing

# Coverage должен быть >= предыдущего значения
```

## Output Format

```markdown
## Test Results: $ARGUMENTS

**Date:** [timestamp]
**Environment:** [dev/staging/prod]
**Test Command:** `[command used]`

---

### Summary

| Type | Total | Pass | Fail | Skip |
|------|-------|------|------|------|
| Unit | X | X | X | X |
| Integration | X | X | X | X |
| E2E | X | X | X | X |

**Overall Status:** ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

---

### Coverage

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Lines | X% | Y% | +/-Z% |
| Branches | X% | Y% | +/-Z% |
| Functions | X% | Y% | +/-Z% |

---

### Scenarios Tested

| # | Scenario | Expected | Actual | Status |
|---|----------|----------|--------|--------|
| 1 | Happy path | success | success | ✅ |
| 2 | Empty input | error | error | ✅ |
| 3 | Invalid | error | crashed | ❌ |

---

### Failed Tests

1. **`test_name`**
   - **Expected:** [what should happen]
   - **Actual:** [what happened]
   - **Stack trace:**
     ```
     [error details]
     ```
   - **Likely cause:** [analysis]

---

### Bugs Found

1. **[CRITICAL/HIGH/MEDIUM/LOW]** [Title]
   - **Steps to reproduce:**
     1. [step 1]
     2. [step 2]
   - **Expected:** [expected behavior]
   - **Actual:** [actual behavior]
   - **Screenshot:** [if available]

---

### Recommendations

- [ ] Fix bug: [description]
- [ ] Add test for: [missing scenario]
- [ ] Increase coverage for: [area]

---

### Next Steps

- [ ] Fix failing tests → `/project:implement`
- [ ] Code review → `/project:review`
- [ ] Or mark as done
```

## Cleanup

```bash
# Stop dev server if started
if [ -n "$DEV_PID" ]; then
  kill $DEV_PID 2>/dev/null
fi
```

## Important Notes

- Тестируй как **РЕАЛЬНЫЙ ПОЛЬЗОВАТЕЛЬ**, не как разработчик
- Не полагайся только на unit тесты — E2E критичны
- Документируй **ВСЕ** найденные проблемы
- Screenshots помогают понять visual bugs
- Flaky tests требуют особого внимания