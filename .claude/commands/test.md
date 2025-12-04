# Test Feature: $ARGUMENTS

Протестируй фичу "$ARGUMENTS" end-to-end как реальный пользователь.

## Process

### 1. Подготовка
```bash
# Запусти dev server если не запущен
npm run dev  # или python -m uvicorn main:app --reload

# Проверь что сервер отвечает
curl http://localhost:3000/health
```

### 2. E2E Testing

#### Если есть Puppeteer MCP:
1. Открой приложение в браузере
2. Выполни user flow для "$ARGUMENTS"
3. Сделай скриншоты ключевых шагов
4. Проверь визуально что всё корректно

#### Если нет browser automation:
```bash
# Для API endpoints
curl -X GET http://localhost:3000/api/endpoint
curl -X POST http://localhost:3000/api/endpoint -d '{"key": "value"}'

# Проверь responses
```

### 3. Unit/Integration Tests
```bash
# Запусти тесты для конкретной фичи
npm run test -- --grep "$ARGUMENTS"
# или
pytest -k "$ARGUMENTS" -v
```

### 4. Test Scenarios

Для фичи "$ARGUMENTS" проверь:

| Scenario | Expected | Status |
|----------|----------|--------|
| Happy Path | [expected result] | ✅/❌ |
| Empty Input | [expected error] | ✅/❌ |
| Invalid Input | [expected error] | ✅/❌ |
| Edge Case 1 | [expected result] | ✅/❌ |
| Concurrent Access | [expected behavior] | ✅/❌ |

## Output Format

```markdown
## Test Results: $ARGUMENTS

**Overall Status:** ✅ Pass / ⚠️ Partial / ❌ Fail

**Date:** [timestamp]

### Environment
- Server: [running/stopped]
- Browser: [if applicable]
- Test Framework: [pytest/vitest/etc]

### Scenarios Tested

| # | Scenario | Expected | Actual | Status |
|---|----------|----------|--------|--------|
| 1 | Happy path | ... | ... | ✅ |
| 2 | Edge case | ... | ... | ⚠️ |

### Screenshots
[Если доступны - описание что на скриншоте]

### Issues Found
1. **[Severity]** Description
   - Steps to reproduce
   - Expected vs Actual
   
### Test Coverage
- Unit tests: X passing, Y failing
- Integration tests: X passing, Y failing

### Recommendations
- [What needs to be fixed]
- [What tests to add]
```

## Important
- Тестируй как РЕАЛЬНЫЙ пользователь
- Не полагайся только на unit тесты
- Проверяй визуально если возможно
- Документируй ВСЕ найденные проблемы
