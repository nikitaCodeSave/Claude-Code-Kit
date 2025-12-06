---
description: Показывает текущий статус проекта. Использовать для быстрого обзора, при вопросах "что дальше", "где мы", или "status". Поддерживает компактный режим.
allowed-tools: Read, Bash, Grep, Glob
---
# Статус проекта

> `$ARGUMENTS`:
> - `compact` или `short` — краткий вывод
> - пусто — полный статус

Покажи текущий статус проекта.

## Сбор контекста

При вызове СНАЧАЛА (с timeout для безопасности):

```bash
# 1. Текущая задача
cat .claude-workspace/current-task.md 2>/dev/null | head -15 || echo "No active task"

# 2. Git status (быстро)
timeout 5 git status --short 2>/dev/null | head -10

# 3. Тесты (quick check - только список)
timeout 10 pytest --co -q 2>/dev/null | tail -5 || echo "Tests: unknown"
```

## Обработка отсутствующих файлов

| Файл | Если отсутствует |
|------|------------------|
| features.json | Показать "No features tracked" |
| current-task.md | Показать "No active task" |
| progress.md | Показать "No history" |

**ВАЖНО:** Если директория `.claude-workspace/` НЕ существует:

```markdown
⚠️ Workspace не инициализирован

Запустите `/init-project` для инициализации:
- Создаст структуру .claude-workspace/
- Настроит файлы отслеживания
- Проверит конфигурацию проекта
```

## Сбор информации

```bash
# 1. Текущая задача
TASK=$(cat .claude-workspace/current-task.md 2>/dev/null | head -20) || TASK="No active task"

# 2. Последний прогресс
PROGRESS=$(cat .claude-workspace/progress.md 2>/dev/null | tail -30) || PROGRESS="No history"

# 3. Git status
GIT_STATUS=$(git status --short 2>/dev/null)
GIT_LOG=$(git log --oneline -5 2>/dev/null)
GIT_BRANCH=$(git branch --show-current 2>/dev/null)

# 4. Тесты (quick check с timeout)
TEST_RESULT=$(timeout 30 pytest --co -q 2>&1 | tail -5 || echo "Tests not configured")

# 5. Features
FEATURES=$(cat .claude-workspace/features.json 2>/dev/null | jq -r '.features[] | "\(.status): \(.name)"' 2>/dev/null) || FEATURES="No features tracked"
```

## Формат вывода

### Если КОМПАКТНЫЙ режим (`$ARGUMENTS` содержит "compact" или "short"):

```markdown
## Статус (компактный)

**Задача:** [название задачи или "Нет"]
**Прогресс:** [X/Y шагов]
**Ветка:** `[branch]`
**Изменения:** [количество незакоммиченных или "чисто"]
**Тесты:** OK/FAIL

**Далее:** [рекомендуемое действие]
```

### Если ПОЛНЫЙ режим (по умолчанию):

```markdown
## Статус проекта

**Сгенерировано:** [timestamp]

---

### Текущая задача
[Из current-task.md или "Нет активной задачи"]

**Прогресс:** [X/Y шагов выполнено]
**Следующий шаг:** [следующий незавершённый шаг]

---

### Недавняя активность
[Последние 5 записей из progress.md]

---

### Обзор фич

| Статус | Фича |
|--------|------|
| Готово | feature1 |
| В работе | feature2 |
| Запланировано | feature3 |

---

### Статус Git

**Ветка:** `[текущая ветка]`

**Незакоммиченные изменения:**
[список файлов или "Рабочее дерево чистое"]

**Недавние коммиты:**
1. `abc123` feat: описание — 2ч назад
2. `def456` fix: описание — 5ч назад
...

---

### Тесты
```
[резюме вывода тестов]
```
- Прошло: X
- Упало: Y
- Покрытие: Z% (если доступно)

---

### Предупреждения
[Блокеры, проблемы или замечания]

---

### Рекомендуемые следующие шаги

1. **[Самое важное действие]**
   - Команда: `/xxx`
2. [Второй приоритет]
3. [Третий приоритет]
```

## Быстрые действия

После показа статуса, предложи релевантные команды:

| Ситуация | Рекомендация |
|----------|--------------|
| Workspace не создан | `/init-project` |
| Нет текущей задачи | `/create-plan [feature]` |
| Есть план, не начат | `/implement` |
| Есть изменения, готово | `/review` |
| Есть failed tests | `/test [feature]` |
| Есть uncommitted | `git add . && git commit` |

## Ограничения

### ЗАПРЕЩЕНО
- Модифицировать файлы (read-only команда!)
- Запускать полные тесты (только --collect-only)
- Долгие операции без timeout

### ОБЯЗАТЕЛЬНО
- Использовать timeout для всех команд
- Graceful handling если файлы отсутствуют
- Показать конкретный next step

## Вывод

Заверши сообщением:
```
Рекомендуется: [команда] — [почему]
```
