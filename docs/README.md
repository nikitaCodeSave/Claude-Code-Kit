# Claude Code Kit

Шаблонный проект для эффективной работы с Claude Code. Предоставляет структуру агентов, slash-команды и единую систему отслеживания состояния.

## Для кого этот проект

- **Разработчики**, использующие Claude Code для повседневной работы
- **Команды**, которым нужна стандартизированная структура проекта
- **Новички** в Claude Code, которые хотят изучить best practices

## Быстрый старт

### 1. Скопируйте шаблон

```bash
# Клонируйте репозиторий
git clone https://github.com/anthropics/claude-code-kit.git my-project
cd my-project

# Или скопируйте только нужные директории в существующий проект
cp -r claude-code-kit/.claude your-project/
cp -r claude-code-kit/.claude-workspace your-project/
cp claude-code-kit/CLAUDE.md your-project/
```

### 2. Начните работу

```bash
# Запустите Claude Code
claude

# Создайте план для новой фичи
/plan-task user authentication

# После одобрения — реализуйте
/implement

# Код-ревью
/review-task

# Завершите задачу
/done
```

## Структура проекта

```
.
├── .claude/                    # Конфигурация Claude Code
│   ├── agents/                 # Специализированные агенты (4)
│   │   ├── dev-agent.md        # TDD разработчик
│   │   ├── review-agent.md     # Код-ревьюер
│   │   ├── explore-agent.md    # Разведчик кодовой базы
│   │   └── doc-agent.md        # Документатор
│   ├── commands/               # Slash-команды (4)
│   │   ├── plan-task.md        # Планирование задачи
│   │   ├── implement.md        # Реализация по плану
│   │   ├── review-task.md      # Код-ревью
│   │   └── done.md             # Завершение задачи
│   └── settings.local.json     # Permissions и hooks
│
├── .claude-workspace/          # Рабочие файлы
│   ├── state.json              # Единый файл состояния
│   └── archive/                # Архив завершённых задач
│
├── docs/                       # Документация
│   ├── README.md               # Этот файл
│   ├── WORKFLOW.md             # Процессы разработки
│   ├── COMMANDS.md             # Справка по командам
│   └── AGENTS.md               # Справка по агентам
│
└── CLAUDE.md                   # Основные инструкции для Claude
```

## Workflow

Линейный процесс разработки:

```
/plan-task → (approve) → /implement → /review-task → /done → merge
```

### Основные команды

| Команда | Когда использовать |
|---------|-------------------|
| `/plan-task [feature]` | Перед реализацией. Флаги: `--quick`, `--issue N` |
| `/implement` | После одобрения плана |
| `/review-task` | После реализации, перед merge |
| `/done` | После APPROVED ревью |

Подробнее: [COMMANDS.md](./COMMANDS.md)

### Агенты

| Агент | Модель | Роль |
|-------|--------|------|
| `dev-agent` | sonnet | TDD разработка: RED → GREEN → REFACTOR → COMMIT |
| `review-agent` | sonnet | Независимый код-ревью |
| `explore-agent` | haiku | Быстрая разведка по кодовой базе |
| `doc-agent` | sonnet | Документация |

Подробнее: [AGENTS.md](./AGENTS.md)

## state.json

Единый файл состояния заменяет множество отдельных файлов:

```json
{
  "project": "project-name",
  "currentTask": {
    "id": "F001",
    "name": "Feature name",
    "status": "planned|in_progress|review|done",
    "complexity": "S|M|L|XL",
    "steps": [
      {"id": 1, "name": "Step 1", "completed": false}
    ]
  },
  "features": [
    {"id": "F001", "name": "Feature", "status": "done"}
  ],
  "progress": [
    {"timestamp": "...", "type": "PLAN|IMPLEMENT|REVIEW|COMPLETE", "message": "..."}
  ],
  "decisions": [
    {"id": "ADR-001", "title": "Decision", "decision": "..."}
  ]
}
```

## TDD Workflow

Разработка ведётся по Test-Driven Development:

```
1. WRITE TEST (RED)    — тест должен упасть
2. WRITE CODE (GREEN)  — минимум кода для прохождения
3. REFACTOR            — улучшение без изменения поведения
4. COMMIT              — атомарный коммит
5. UPDATE state.json   — отметить шаг как выполненный
```

## Правила работы

1. **НАЧАЛО сессии**: прочитай `state.json` для контекста
2. **КОНЕЦ сессии**: обнови `state.json` с результатами
3. Работай над **ОДНОЙ** задачей за раз
4. Используй `/plan-task` для задач > 50 строк кода
5. Используй `/review-task` после реализации, перед merge

## Документация

- [WORKFLOW.md](./WORKFLOW.md) — детальное описание процессов
- [COMMANDS.md](./COMMANDS.md) — справка по командам
- [AGENTS.md](./AGENTS.md) — справка по агентам

## Адаптация под свой проект

1. Отредактируйте `CLAUDE.md` — добавьте специфику вашего проекта
2. Настройте `.claude/settings.local.json` — permissions и hooks
3. Добавьте свои команды в `.claude/commands/`
4. Добавьте свои агенты в `.claude/agents/`

## Лицензия

MIT License
