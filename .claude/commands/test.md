---
description: E2E тестирование фичи. Использовать после реализации для проверки работы как реальный пользователь. Поддерживает автоматическое и ручное тестирование.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
# Тестирование фичи: $ARGUMENTS

> `$ARGUMENTS` — название фичи для тестирования
> Пример: `/test user login` → $ARGUMENTS = "user login"

Протестируй фичу "$ARGUMENTS" end-to-end как реальный пользователь.

## Сбор контекста

При вызове СНАЧАЛА:

```bash
# 1. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null | head -15

# 2. Существующие тесты
ls tests/ 2>/dev/null || ls test/ 2>/dev/null

# 3. Pytest конфигурация
cat pytest.ini 2>/dev/null || cat pyproject.toml 2>/dev/null | grep -A 10 "\[tool.pytest"

# 4. Найти тесты для фичи
rg "$ARGUMENTS" tests/ 2>/dev/null | head -10
```

## Подготовка к тестированию

```bash
# 1. Проверь что dev server можно запустить (если FastAPI/Flask)
if [ -f "pyproject.toml" ]; then
  echo "Starting dev server..."
  uvicorn main:app --reload &
  DEV_PID=$!
  sleep 3

  # Health check
  curl -s http://localhost:8000/health || curl -s http://localhost:8000/docs | head -5
fi

# 2. Определи test framework
cat pyproject.toml 2>/dev/null | grep -A 5 "pytest\|unittest"

# 3. Найди существующие тесты для фичи
rg "def test.*$ARGUMENTS" tests/ 2>/dev/null | head -10
```

## Процесс тестирования

### 1. Unit/Integration тесты

```bash
# Запусти тесты для конкретной фичи
pytest -k "$ARGUMENTS" -v --cov

# Если нет специфичных тестов, запусти все
pytest tests/ -v

# С coverage report
pytest --cov=src --cov-report=term-missing
```

```python
# Примеры pytest тестов

# Unit test
def test_feature_returns_expected():
    result = feature_function("input")
    assert result == "expected"

# Integration test с fixture
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_api_endpoint(client):
    response = client.get("/api/endpoint")
    assert response.status_code == 200

# Async test
@pytest.mark.asyncio
async def test_async_feature():
    result = await async_function()
    assert result is not None
```

### 2. E2E тестирование

#### С автоматизацией браузера (Playwright/Puppeteer MCP)

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

#### Без автоматизации браузера (API тестирование)

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

### 3. Матрица тестовых сценариев

Для фичи "$ARGUMENTS" проверь:

| # | Сценарий | Входные данные | Ожидаемый результат | Статус |
|---|----------|----------------|---------------------|--------|
| 1 | Основной путь | валидные данные | успех | ⬜ |
| 2 | Пустой ввод | `""`, `null` | ошибка валидации | ⬜ |
| 3 | Невалидный ввод | неверный тип/формат | ошибка типа | ⬜ |
| 4 | Граница мин | минимально допустимое | успех/ошибка | ⬜ |
| 5 | Граница макс | максимально допустимое | успех/ошибка | ⬜ |
| 6 | Спецсимволы | `<script>`, `'; DROP` | санитизировано | ⬜ |
| 7 | Параллельность | параллельные запросы | нет race condition | ⬜ |
| 8 | Сетевая ошибка | timeout/500 | корректная обработка | ⬜ |

### 4. Проверка покрытия

```bash
# Проверь coverage после тестов
pytest --cov=src --cov-report=term-missing

# Coverage должен быть >= предыдущего значения
# Минимум 80% для новых файлов
```

## Ограничения по времени

| Тип теста | Таймаут | Общее время |
|-----------|---------|-------------|
| Unit | 5 сек/тест | < 30 сек total |
| Integration | 30 сек/тест | < 2 мин total |
| E2E | 60 сек/тест | < 5 мин total |

## Обработка ошибок

| Проблема | Решение |
|----------|---------|
| Server already running | `lsof -i :8000` и kill, или другой порт |
| Flaky test | Перезапустить 3 раза, если всё ещё flaky → `@pytest.mark.skip` |
| Timeout | Увеличить timeout или оптимизировать тест |
| Missing fixtures | Проверить `conftest.py` |
| Import errors | Проверить `PYTHONPATH` и `__init__.py` |

## Формат вывода

```markdown
## Результаты тестирования: $ARGUMENTS

**Дата:** [timestamp]
**Окружение:** [dev/staging/prod]
**Команда тестирования:** `[использованная команда]`

---

### Резюме

| Тип | Всего | Прошло | Упало | Пропущено |
|-----|-------|--------|-------|-----------|
| Unit | X | X | X | X |
| Integration | X | X | X | X |
| E2E | X | X | X | X |

**Общий статус:** ✅ ПРОЙДЕНО / ⚠️ ЧАСТИЧНО / ❌ ПРОВАЛЕНО

---

### Покрытие

| Метрика | До | После | Дельта |
|---------|-----|-------|--------|
| Строки | X% | Y% | +/-Z% |
| Ветви | X% | Y% | +/-Z% |
| Функции | X% | Y% | +/-Z% |

---

### Протестированные сценарии

| # | Сценарий | Ожидаемо | Фактически | Статус |
|---|----------|----------|------------|--------|
| 1 | Основной путь | успех | успех | ✅ |
| 2 | Пустой ввод | ошибка | ошибка | ✅ |
| 3 | Невалидный | ошибка | крэш | ❌ |

---

### Проваленные тесты

1. **`test_name`**
   - **Ожидалось:** [что должно было произойти]
   - **Фактически:** [что произошло]
   - **Stack trace:**
     ```
     [детали ошибки]
     ```
   - **Вероятная причина:** [анализ]

---

### Найденные баги

1. **[КРИТИЧНО/ВЫСОКО/СРЕДНЕ/НИЗКО]** [Заголовок]
   - **Шаги воспроизведения:**
     1. [шаг 1]
     2. [шаг 2]
   - **Ожидалось:** [ожидаемое поведение]
   - **Фактически:** [фактическое поведение]
   - **Скриншот:** [если доступен]

---

### Рекомендации

- [ ] Исправить баг: [описание]
- [ ] Добавить тест для: [недостающий сценарий]
- [ ] Увеличить покрытие для: [область]

---

### Следующие шаги

- [ ] Исправить проваленные тесты → `/implement`
- [ ] Код-ревью → `/code-review`
- [ ] Или отметить как готово
```

## Очистка

```bash
# Stop dev server if started
if [ -n "$DEV_PID" ]; then
  kill $DEV_PID 2>/dev/null
fi
```

## Ограничения

### ЗАПРЕЩЕНО
- Тесты зависящие друг от друга
- Hardcoded test data в коде (используй fixtures)
- `time.sleep()` в тестах (используй mocking)
- Пропускать edge cases
- Игнорировать flaky tests

### ОБЯЗАТЕЛЬНО
- Каждый тест независим
- Fixtures для shared data
- Cleanup после тестов
- Документировать все найденные баги

## Чеклист качества

Перед завершением проверь:

- [ ] Все сценарии из матрицы протестированы
- [ ] Coverage не ниже baseline
- [ ] Нет flaky tests
- [ ] Все баги задокументированы
- [ ] Dev server остановлен

## Важные заметки

- Тестируй как **РЕАЛЬНЫЙ ПОЛЬЗОВАТЕЛЬ**, не как разработчик
- Не полагайся только на unit тесты — E2E критичны
- Документируй **ВСЕ** найденные проблемы
- Screenshots помогают понять visual bugs
- Flaky tests требуют особого внимания

## Обновление прогресса

После завершения тестирования добавь запись в `.claude-workspace/progress.md`:

```bash
echo "## $(date '+%Y-%m-%d %H:%M') - Testing: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Feature: $ARGUMENTS" >> .claude-workspace/progress.md
echo "- Status: [PASS/FAIL/PARTIAL]" >> .claude-workspace/progress.md
echo "- Bugs found: [количество или 'none']" >> .claude-workspace/progress.md
echo "" >> .claude-workspace/progress.md
```