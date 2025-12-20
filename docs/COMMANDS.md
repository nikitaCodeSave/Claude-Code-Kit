# Slash Commands

Справочник по slash-командам Claude Code Kit.

## Обзор команд

| Команда | Когда использовать |
|---------|-------------------|
| `/plan-task [feature]` | Перед реализацией. Флаги: `--quick`, `--issue N` |
| `/implement` | После одобрения плана |
| `/review-task` | После реализации, перед merge. Аргументы: `N`, `staged`, `branch` |
| `/done` | После APPROVED ревью |

## Линейный workflow

```
/plan-task → (approve) → /implement → /review-task → /done → merge
```

---

## /plan-task

**Файл:** `.claude/commands/plan-task.md`

### Описание

Создаёт план реализации задачи. Объединяет функциональность старых команд `/create-plan`, `/quick-fix`, `/fix-issue`.

### Режимы работы

| Аргумент | Режим | Сложность | Описание |
|----------|-------|-----------|----------|
| `[feature]` | Standard | Auto | Полный цикл планирования |
| `--quick [bug]` | Quick Fix | S | Мелкий баг < 20 строк |
| `--issue N` | GitHub Issue | Auto | Анализ и фикс issue #N |

### Примеры использования

```bash
# Стандартное планирование
/plan-task user authentication

# Быстрый фикс мелкого бага
/plan-task --quick email validation broken

# Исправление GitHub issue
/plan-task --issue N
```

### Что делает

1. **Context Discovery:**
   - Читает `state.json.currentTask`
   - Проверяет git status
   - Изучает структуру проекта

2. **Анализ задачи:**
   - Определяет сложность (S/M/L/XL)
   - Находит релевантный код
   - Использует WebSearch для выбора технологий

3. **Создание плана:**
   - Записывает в `state.json.currentTask`
   - Добавляет в `state.json.progress`
   - Если выбор из альтернатив — добавляет ADR в `decisions`

### Формат вывода

```markdown
**План готов:**
- **Задача:** [название]
- **Сложность:** [S/M/L/XL]
- **Шагов:** N
- **Ключевые файлы:** [2-3 файла]

**Начать реализацию с `/implement`?**
```

### Правила для шагов

- Max 12 шагов (если больше → разбить на подзадачи)
- Каждый шаг ≤ 30 минут работы
- Каждый шаг включает тесты
- Один шаг = один атомарный коммит

### Ограничения

**ЗАПРЕЩЕНО:**
- Писать код (только план)
- Начинать реализацию без подтверждения
- Более 12 шагов в одном плане

**ОБЯЗАТЕЛЬНО:**
- Проверить currentTask перед созданием
- Включить тесты в каждый шаг
- Дождаться подтверждения

---

## /implement

**Файл:** `.claude/commands/implement.md`

### Описание

Реализует задачу из `state.json.currentTask` через TDD подход. Делегирует работу `dev-agent`.

### Когда использовать

- После одобрения плана от `/plan-task`
- Когда есть готовый план в `state.json.currentTask`

### Что делает

1. **Pre-check:**
   - Проверяет наличие плана
   - Проверяет baseline (тесты проходят)
   - Обновляет статус на `in_progress`

2. **Делегирует dev-agent:**
   - Для каждого шага выполняет TDD цикл
   - Атомарные коммиты после каждого шага
   - Обновляет `state.json` после каждого шага

3. **Post-check:**
   - Все тесты проходят
   - Linting без ошибок
   - Обновляет статус на `review`

### Формат вывода

```markdown
## Implementation Complete

| Metric | Value |
|--------|-------|
| Steps completed | X/Y |
| Tests added | Z |
| Files changed | W |
| Commits | N |
| Coverage | M% |

### Status: READY_FOR_REVIEW

### Next Steps
- Запустите `/review-task` для код-ревью
```

### Ограничения

**ЗАПРЕЩЕНО:**
- Пропускать TDD цикл
- Коммитить нерабочий код
- Менять план без согласования

**ОБЯЗАТЕЛЬНО:**
- Каждый шаг = один атомарный коммит
- Обновлять state.json после каждого шага
- Все тесты проходят перед коммитом

---

## /review-task

**Файл:** `.claude/commands/review-task.md`

### Описание

Проводит независимое код-ревью недавних изменений. Делегирует работу `review-agent`.

### Аргументы

| Аргумент | Описание |
|----------|----------|
| (пусто) | Auto-detect из state.json (последние ~5 коммитов) |
| `N` | Последние N коммитов |
| `staged` | Только staged changes |
| `branch` | Все коммиты ветки относительно main |

### Примеры использования

```bash
# Автоматический scope
/review-task

# Последние 3 коммита
/review-task 3

# Только staged changes
/review-task staged

# Вся ветка
/review-task branch
```

### Что делает

1. **Понимает intent:**
   - Читает план из `state.json.currentTask`
   - Собирает diff и статистику

2. **Автоматические проверки:**
   - Тесты
   - Linting
   - Type checking

3. **Security scan:**
   - Secrets detection
   - SQL/Command injection
   - Console.log в production

4. **Детальный обзор:**
   - Проверяет каждый файл как независимый ревьюер

### Auto-REJECT критерии

| Находка | Действие |
|---------|----------|
| Hardcoded secrets | REJECT |
| SQL/Command injection | REJECT |
| console.log в production | CHANGES REQUESTED |
| Нет тестов | CHANGES REQUESTED |

### Формат вывода

```markdown
## Code Review

**Scope:** [что проверено]
**Verdict:** APPROVED | CHANGES REQUESTED | REJECTED
**Quality:** 4/5

### Автоматические проверки

| Check | Status |
|-------|--------|
| Tests | ✅/❌ |
| Lint | ✅/❌ |
| Security | ✅/⚠️/❌ |

### Findings

#### Critical (must fix)
1. **[Title]** — `file:line` — [issue] — [solution]

### What's Good
- [положительные аспекты]

### Next Steps
При APPROVED: Запустите `/done` для завершения задачи.
При CHANGES REQUESTED: Исправьте findings и запустите `/review-task` повторно.
```

### Ограничения

**ОБЯЗАТЕЛЬНО:**
- Быть объективным
- Объяснять ПОЧЕМУ что-то плохо
- Предлагать конкретные решения

**ЗАПРЕЩЕНО:**
- Модифицировать файлы
- Approve код с CRITICAL findings

---

## /done

**Файл:** `.claude/commands/done.md`

### Описание

Завершает текущую задачу: архивирует план, обновляет `state.json`, очищает workspace для следующей задачи.

### Когда использовать

- После получения APPROVED вердикта от `/review-task`
- Когда задача полностью завершена и готова к merge

### Что делает

1. **Валидация:**
   - Проверяет наличие задачи
   - Проверяет git status
   - Проверяет завершённость шагов

2. **Архивация:**
   - Создаёт файл в `archive/YYYY-MM-DD-slug.md`
   - Сохраняет полный план и результаты

3. **Обновление state.json:**
   - `currentTask` = null
   - `features[]` обновляется: status → "done"
   - `progress[]` += COMPLETE entry

4. **Git commit** (опционально):
   - Коммитит изменения в `.claude-workspace/`

### Формат вывода

```markdown
## Task Completed

**Name:** [TASK_NAME]
**ID:** [TASK_ID]
**Date:** [TIMESTAMP]

### Archived
`[ARCHIVE_PATH]`

### Updated
- state.json: currentTask → null
- features[]: status → "done"
- progress[]: +1 COMPLETE entry

### Stats
- Steps: [completed]/[total]
- Commits: [N]
- Files changed: [M]

---

**Next Steps:**
- `/plan-task [new feature]` — start new task
```

### Ограничения

**ЗАПРЕЩЕНО:**
- Удалять задачу без архивации
- Перезаписывать существующие архивы
- Завершать с незакоммиченными изменениями

**ОБЯЗАТЕЛЬНО:**
- Сохранить полные данные в архив
- Обновить state.json
- Показать summary

---

## Выбор команды

```
                    ┌─────────────────┐
                    │   Новая задача  │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │   Размер?       │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           v                 v                 v
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  < 20 LOC    │  │  20-500 LOC  │  │  GitHub      │
    │              │  │              │  │  Issue       │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           v                 v                 v
    ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
    │/plan-task --quick  │  │/plan-task feature  │  │/plan-task --issue  │
    └────────────────────┘  └────────────────────┘  └────────────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             v
                    ┌─────────────────┐
                    │   /implement    │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │  /review-task   │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │     /done       │
                    └─────────────────┘
```
