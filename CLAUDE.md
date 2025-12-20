# CLAUDE.md

Инструкции для Claude Code при работе с этим репозиторием.

## Обзор

Claude Code Kit — шаблонный проект со структурой агентов и slash-команд для работы с Claude Code. Копируйте `.claude/` и `.claude-workspace/` в свои проекты.

## Правила сессии

1. **НАЧАЛО**: Прочитай `.claude-workspace/state.json` для контекста
2. **КОНЕЦ**: Обнови `state.json` с результатами работы
3. Работай над ОДНОЙ задачей за раз
4. Используй `/plan-task` для задач > 50 строк кода
5. Используй `/review-task` после реализации, перед merge

## Команды

| Команда | Когда использовать |
|---------|-------------------|
| `/plan-task [feature]` | Перед реализацией. Флаги: `--quick` (< 20 LOC), `--issue N` (GitHub) |
| `/implement` | После одобрения плана. Запускает dev-agent с TDD |
| `/review-task` | После реализации. Аргументы: `N` (коммиты), `staged`, `branch` |
| `/done` | После APPROVED ревью. Архивирует задачу |

## Workflow

```
/plan-task → approve → /implement → /review-task → /done → merge
```

**TDD цикл (dev-agent):**
1. Напиши тест → должен УПАСТЬ (RED)
2. Напиши минимум кода → тест ПРОХОДИТ (GREEN)
3. Рефактори (REFACTOR)
4. `git commit`
5. Обнови `state.json`

## Агенты

| Агент | Модель | Роль |
|-------|--------|------|
| `dev-agent` | sonnet | TDD разработка: тесты + код + коммиты |
| `review-agent` | sonnet | Независимый код-ревью |
| `explore-agent` | haiku | Быстрая разведка по коду |
| `doc-agent` | sonnet | Документация |

## Ключевые файлы

```
.claude-workspace/
├── state.json              # Единый файл состояния
└── archive/                # Завершённые задачи

.claude/
├── agents/                 # Определения агентов
├── commands/               # Slash-команды
└── settings.local.json     # Permissions и hooks
```

## state.json

```json
{
  "project": "project-name",
  "currentTask": {
    "id": "F001",
    "name": "Feature name",
    "status": "planned|in_progress|review|done",
    "complexity": "S|M|L|XL",
    "steps": [{"id": 1, "name": "...", "completed": false}]
  },
  "features": [{"id": "F001", "name": "...", "status": "done"}],
  "progress": [{"timestamp": "...", "type": "PLAN|IMPLEMENT|REVIEW|COMPLETE", "message": "..."}],
  "decisions": [{"id": "ADR-001", "title": "...", "decision": "..."}]
}
```

## Git-конвенции

**Формат:** `type(scope): description`

**Типы:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

## Безопасность

### Автоматически разрешено
- Git: add, commit, checkout, pull, stash, rm, branch
- Python: pytest, python, python3
- Node: npm, yarn, pnpm, bun, jest, vitest
- Docker: stop, rm

### Требует подтверждения
- SSH подключения
- Docker exec/run

### Заблокировано (hooks)
- `rm -rf /`, `~`, `*`, `.`
- `git reset --hard`, `push --force`, `clean -fd`
- `curl|sh`, `wget|sh`
- `chmod 000/777`
- `mkfs`, `dd of=/dev`
