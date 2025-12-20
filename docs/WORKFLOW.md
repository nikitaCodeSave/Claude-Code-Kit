# Workflow

Описание процессов разработки в Claude Code Kit.

## Линейный workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DEVELOPMENT CYCLE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌────────────┐   ┌──────────┐   ┌─────────────┐   ┌──────────┐            │
│   │/plan-task  │──▶│/implement│──▶│/review-task │──▶│  /done   │──▶ merge   │
│   └─────┬──────┘   └────┬─────┘   └──────┬──────┘   └────┬─────┘            │
│        │              │              │              │                   │
│        v              v              v              v                   │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│   │ state.   │   │  Atomic  │   │ APPROVED │   │ archive/ │            │
│   │ json     │   │ Commits  │   │  /REJECT │   │ cleanup  │            │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘            │
│                                                                         │
│   state.json.currentTask.status:                                        │
│   planned ──▶ in_progress ──▶ review ──▶ done                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## TDD Workflow

Test-Driven Development — основа разработки в `dev-agent`:

```
┌─────────────────────────────────────────────┐
│                TDD CYCLE                     │
├─────────────────────────────────────────────┤
│                                             │
│   1. WRITE TEST (RED)                       │
│   ┌─────────────────────────────────────┐   │
│   │ - Тест описывает expected behavior  │   │
│   │ - Запусти тест                      │   │
│   │ - Тест ДОЛЖЕН УПАСТЬ               │   │
│   └────────────────┬────────────────────┘   │
│                    │                        │
│                    v                        │
│   2. WRITE CODE (GREEN)                     │
│   ┌─────────────────────────────────────┐   │
│   │ - Напиши минимум кода               │   │
│   │ - Только для прохождения теста      │   │
│   │ - Тест ДОЛЖЕН ПРОЙТИ               │   │
│   └────────────────┬────────────────────┘   │
│                    │                        │
│                    v                        │
│   3. REFACTOR                               │
│   ┌─────────────────────────────────────┐   │
│   │ - Улучши читаемость                 │   │
│   │ - Убери дублирование                │   │
│   │ - Тесты всё ещё проходят           │   │
│   └────────────────┬────────────────────┘   │
│                    │                        │
│                    v                        │
│   4. COMMIT                                 │
│   ┌─────────────────────────────────────┐   │
│   │ - git add .                         │   │
│   │ - git commit -m "type(scope): msg"  │   │
│   │ - Один шаг = один коммит            │   │
│   └────────────────┬────────────────────┘   │
│                    │                        │
│                    v                        │
│   5. UPDATE state.json                      │
│   ┌─────────────────────────────────────┐   │
│   │ - step.completed = true             │   │
│   │ - progress[] += new entry           │   │
│   └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## state.json

Единый файл состояния заменяет множество отдельных Markdown файлов:

```json
{
  "project": "project-name",
  "version": "2.0",

  "currentTask": {
    "id": "F001",
    "name": "Feature name",
    "status": "planned|in_progress|review|done",
    "complexity": "S|M|L|XL",
    "description": "Описание задачи",
    "steps": [
      {
        "id": 1,
        "name": "Step name",
        "description": "Что сделать",
        "files": ["path/to/file"],
        "tests": "Что проверить",
        "completed": false,
        "completedAt": null
      }
    ],
    "scope": {
      "includes": ["что включено"],
      "excludes": ["что НЕ включено"]
    },
    "successCriteria": [
      "Критерий успеха 1",
      "Критерий успеха 2"
    ],
    "risks": [
      {
        "risk": "Описание риска",
        "probability": "low|medium|high",
        "mitigation": "Как минимизировать"
      }
    ],
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z"
  },

  "features": [
    {
      "id": "F001",
      "name": "Feature name",
      "status": "planned|in_progress|review|done",
      "priority": 1,
      "completedAt": null,
      "archivePath": null
    }
  ],

  "progress": [
    {
      "timestamp": "2025-01-01T00:00:00Z",
      "type": "PLAN|IMPLEMENT|REVIEW|COMPLETE|BLOCKED",
      "taskId": "F001",
      "message": "Описание действия"
    }
  ],

  "decisions": [
    {
      "id": "ADR-001",
      "title": "Название решения",
      "status": "accepted|rejected|deprecated",
      "date": "2025-01-01",
      "context": "Почему возникла необходимость",
      "decision": "Что решили",
      "alternatives": ["Альтернатива 1"],
      "consequences": {
        "positive": ["Плюсы"],
        "negative": ["Минусы"]
      },
      "relatedTaskId": "F001"
    }
  ]
}
```

### Преимущества JSON vs Markdown

| Аспект | JSON | Markdown |
|--------|------|----------|
| Парсинг | Надёжный (jq) | Хрупкий |
| Модификация | Атомарная | Ручная |
| Структура | Чёткая | Произвольная |
| Валидация | Автоматическая | Невозможна |
| Коррупция | Маловероятна | Частая |

## Этапы разработки

### 1. Планирование (`/plan-task`)

```
Входные данные:
  - Описание задачи от пользователя
  - Контекст проекта (CLAUDE.md, state.json)

Процесс:
  1. Изучить существующий код
  2. Найти похожие реализации
  3. Декомпозировать на шаги (max 12)
  4. Оценить риски

Результат:
  - План в state.json.currentTask
  - Запись в state.json.progress
  - ADR в state.json.decisions (если был выбор)
```

### 2. Реализация (`/implement`)

```
Входные данные:
  - План из state.json.currentTask
  - Baseline (тесты проходят)

Процесс (для каждого шага):
  1. Написать тест (RED)
  2. Написать код (GREEN)
  3. Рефакторинг
  4. Коммит
  5. Обновить state.json

Результат:
  - Серия атомарных коммитов
  - Обновлённые тесты
  - state.json.currentTask.status = "review"
```

### 3. Ревью (`/review-task`)

```
Входные данные:
  - Коммиты с реализацией
  - План (что должно было быть сделано)

Процесс:
  1. Понять intent из state.json.currentTask
  2. Проверить код как независимый ревьюер
  3. Запустить автоматические проверки
  4. Security scan

Результат:
  - Статус: APPROVED | CHANGES REQUESTED | REJECTED
  - Список findings с severity
  - Запись в state.json.progress
```

### 4. Завершение (`/done`)

```
Входные данные:
  - APPROVED вердикт от /review-task
  - Полная задача в state.json.currentTask

Процесс:
  1. Валидация завершённости
  2. Создание архива в archive/
  3. Обновление state.json

Результат:
  - Архив в .claude-workspace/archive/
  - state.json.currentTask = null
  - state.json.features[] обновлён
```

## Commit Convention

```
type(scope): description

Types:
- feat: новая функциональность
- fix: исправление бага
- refactor: рефакторинг без изменения поведения
- test: добавление/изменение тестов
- docs: документация
- chore: maintenance tasks

Example:
feat(auth): add JWT token validation

- Add validate_token() function
- Add tests for valid/invalid tokens
- Update auth middleware

Step 3/5 of F002
```

## Правила работы

### Начало сессии

```bash
# 1. Загрузи контекст
cat .claude-workspace/state.json | jq '.currentTask'

# 2. Проверь git status
git status --short
git log --oneline -5
```

### Конец сессии

```bash
# 1. Убедись что state.json актуален
cat .claude-workspace/state.json | jq '.currentTask.steps[] | select(.completed == false)'

# 2. Все изменения закоммичены
git status --short

# 3. Тесты проходят
npm test || pytest
```

### Обязательно

- Работать над **ОДНОЙ** задачей за раз
- Использовать `/plan-task` для задач > 50 строк кода
- Использовать `/review-task` после реализации
- Обновлять state.json после каждого шага
- Атомарные коммиты (один шаг = один коммит)

### Запрещено

- Пропускать написание тестов
- Оставлять код в нерабочем состоянии
- Коммитить с падающими тестами
- Модифицировать тесты чтобы они "прошли"
- Работать над несколькими задачами одновременно

## Диаграмма принятия решений

```
                    ┌─────────────────┐
                    │  Новая задача   │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │  Размер > 20    │
              ┌─────┤    строк?       ├─────┐
              │     └─────────────────┘     │
              │ Нет                         │ Да
              v                             v
    ┌──────────────────────┐        ┌──────────────────────┐
    │ /plan-task --quick   │        │ /plan-task feature   │
    └───────────┬──────────┘        └───────────┬──────────┘
             │                             │
             └──────────────┬──────────────┘
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
              ┌─────────────┴─────────────┐
              │                           │
              v                           v
    ┌─────────────────┐         ┌─────────────────┐
    │    APPROVED     │         │ CHANGES         │
    │                 │         │ REQUESTED       │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             v                           v
    ┌─────────────────┐         ┌─────────────────┐
    │     /done       │         │  Fix issues     │
    └─────────────────┘         └────────┬────────┘
                                         │
                                         └──▶ /review-task
```

## Структура архива

После `/done` задача сохраняется в:

```
.claude-workspace/archive/YYYY-MM-DD-slug.md
```

Содержимое:
```markdown
# Archived Task: [Task Name]

**Completed:** [timestamp]
**Task ID:** [ID]
**Status:** DONE

---

## Task Details
[Данные из state.json.currentTask]

### Steps
- [x] Step 1
- [x] Step 2

### Success Criteria
- [criteria]

---

## Completion Summary

### Commits
[git log]

### Changed Files
[git diff --stat]

### Test Results
[результаты тестов]
```
