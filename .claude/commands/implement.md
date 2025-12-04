# Implement Current Task

Реализуй задачу из `.claude-workspace/current-task.md`.

## Pre-Implementation Checklist

```bash
# 1. Проверь текущую задачу
cat .claude-workspace/current-task.md

# 2. Проверь прогресс
cat .claude-workspace/progress.md

# 3. Убедись что dev environment работает
# [запусти dev server и проверь базовый функционал]
```

## Implementation Process

### Для каждого шага из плана:

1. **Напиши тесты СНАЧАЛА (TDD)**
   - Тест должен описывать expected behavior
   - Запусти тест - он ДОЛЖЕН падать
   - Это подтверждает что тест валидный

2. **Напиши минимальный код для прохождения теста**
   - Не переусложняй
   - Достаточно чтобы тест прошёл

3. **Рефактори если нужно**
   - Убери дублирование
   - Улучши читаемость
   - Тесты всё ещё должны проходить

4. **Закоммить с описательным сообщением**
   ```bash
   git add .
   git commit -m "type(scope): description"
   ```

5. **Обнови tracking файлы**
   - Отметь выполненный шаг в current-task.md
   - Добавь запись в progress.md

## After All Steps Completed

```bash
# Запусти ВСЕ тесты
npm run test  # или pytest

# Запусти linter
npm run lint  # или ruff check .

# Проверь типы
npm run typecheck  # или mypy .
```

Если фича полностью готова:
- Обнови статус в `features.json` на "done"
- Добавь completedAt дату

## Rules
- Работай над ОДНИМ шагом за раз
- НЕ пропускай тесты
- Коммить ЧАСТО (после каждого логического изменения)
- Если что-то сломалось - почини СРАЗУ
- НИКОГДА не оставляй код в нерабочем состоянии

## Output
После завершения покажи:
- Список созданных/изменённых файлов
- Результаты тестов
- Git log последних коммитов
