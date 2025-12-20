---
description: Создаёт план реализации. Объединяет create-plan, quick-fix, fix-issue. Использовать перед реализацией любых задач. Флаги: --quick (мелкий фикс), --issue N (GitHub issue).
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch
---

# /plan $ARGUMENTS

## Режимы работы

**Определить режим по аргументам:**

| Аргумент | Режим | Сложность | Описание |
|----------|-------|-----------|----------|
| `--quick [bug]` | Quick Fix | S | Мелкий баг < 20 строк, без полного плана |
| `--issue N` | GitHub Issue | Auto | Анализ и фикс issue #N |
| `[feature]` | Standard | Auto | Полный цикл планирования |

---

## ШАГ 1: Context Discovery

```bash
# 1. Текущее состояние
cat .claude-workspace/state.json | jq '.currentTask'

# 2. Git status
git status --short
git log --oneline -5

# 3. Структура проекта
tree -L 2 -I 'node_modules|__pycache__|.git|.venv|dist|build' 2>/dev/null || ls -la
```

**Если currentTask не null:**
> ⚠️ **Есть незавершённая задача:** [название]
>
> **Варианты:**
> 1. `/done` — завершить текущую и начать новую
> 2. Продолжить и перезаписать (скажите "да")

---

## ШАГ 2: Анализ задачи

### Режим Quick Fix (`--quick`)

```bash
# Найти файл с багом
rg "[error message or pattern]" --type py -l | head -5
```

Сразу создать минимальный план:
```json
{
  "currentTask": {
    "id": "QF001",
    "name": "Quick fix: [описание]",
    "status": "planned",
    "complexity": "S",
    "steps": [
      {"id": 1, "name": "Fix bug", "completed": false}
    ]
  }
}
```

### Режим GitHub Issue (`--issue N`)

```bash
# Получить информацию об issue
gh issue view N --json title,body,labels,comments
```

Проанализировать:
- Что сломано?
- Как воспроизвести?
- Какие файлы затронуты?

### Режим Standard

**Определить сложность:**

| Размер | Строк кода | Шагов | Подход |
|--------|------------|-------|--------|
| **S** | < 50 | 1-3 | Простой план |
| **M** | 50-200 | 4-6 | Детальный план |
| **L** | 200-500 | 7-10 | Декомпозиция, "think hard" |
| **XL** | > 500 | 10+ | Разбить на несколько планов |

**Исследование:**
```bash
# Существующие паттерны
cat CLAUDE.md 2>/dev/null | head -50

# Похожий код
rg "[relevant pattern]" --type py -C 2 | head -30
```

**WebSearch** (если нужно):
- Выбор между библиотеками
- Незнакомая область
- Best practices

---

## ШАГ 3: Создание плана в state.json

**Обновить state.json:**

```json
{
  "currentTask": {
    "id": "FXXX",
    "name": "[название задачи]",
    "status": "planned",
    "complexity": "S|M|L|XL",
    "steps": [
      {
        "id": 1,
        "name": "[Название шага]",
        "description": "[Что сделать]",
        "files": ["path/to/file"],
        "tests": "[Что проверить]",
        "completed": false,
        "completedAt": null
      }
    ],
    "scope": {
      "includes": ["..."],
      "excludes": ["..."]
    },
    "successCriteria": [
      "Все тесты проходят",
      "Нет ошибок линтера",
      "[Конкретный критерий]"
    ],
    "risks": [
      {"risk": "...", "probability": "low|medium|high", "mitigation": "..."}
    ],
    "createdAt": "[ISO timestamp]",
    "updatedAt": "[ISO timestamp]"
  },
  "features": [
    {
      "id": "FXXX",
      "name": "[название]",
      "status": "planned",
      "priority": 1
    }
  ],
  "progress": [
    {
      "timestamp": "[ISO timestamp]",
      "type": "PLAN",
      "taskId": "FXXX",
      "message": "Created plan: [название]"
    }
  ]
}
```

**Правила для шагов:**
- Max 12 шагов (если больше → разбить на подзадачи)
- Каждый шаг ≤ 30 минут работы
- Каждый шаг включает тесты
- Один шаг = один атомарный коммит

---

## ШАГ 4: ADR (если был выбор из альтернатив)

Если выбран подход из нескольких вариантов, добавить в state.json.decisions:

```json
{
  "id": "ADR-XXX",
  "title": "[Название решения]",
  "status": "accepted",
  "date": "[date]",
  "context": "[Почему возникла необходимость выбора]",
  "decision": "[Что выбрано и почему]",
  "alternatives": ["Вариант A — почему отклонён"],
  "consequences": {
    "positive": ["..."],
    "negative": ["..."]
  },
  "relatedTaskId": "FXXX"
}
```

---

## ШАГ 5: Запрос подтверждения

Показать резюме:

> **План готов:**
> - **Задача:** [название]
> - **Сложность:** [S/M/L/XL]
> - **Шагов:** N
> - **Ключевые файлы:** [2-3 файла]
>
> **Начать реализацию с `/implement`?**

**Дождаться подтверждения.**

---

## Ограничения

### ❌ ЗАПРЕЩЕНО
- Писать код (только план)
- Начинать реализацию без подтверждения
- Шаги длиннее 30 минут
- Пропускать тесты в плане
- Более 12 шагов в одном плане

### ✅ ОБЯЗАТЕЛЬНО
- Проверить currentTask перед созданием нового плана
- Включить тесты в каждый шаг
- Указать риски для M/L/XL задач
- Использовать WebSearch для выбора технологий
- Дождаться подтверждения
