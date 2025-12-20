# CLAUDE.md

Этот файл содержит инструкции для Claude Code при работе с кодом в этом репозитории.

## Обзор

Claude Code Kit — шаблонный проект со структурой, агентами и slash-командами для работы с Claude Code. Копируйте и адаптируйте под свои проекты.

## Правила сессии

1. **НАЧАЛО**: Прочитай `.claude-workspace/state.json` для контекста
2. **КОНЕЦ**: Обнови `state.json` с результатами работы
3. Работай над ОДНОЙ фичей за раз
4. Используй `/plan` для фич > 50 строк кода
5. Используй `/review` после реализации

## Команды

| Команда | Когда использовать |
|---------|-------------------|
| `/plan [feature]` | Перед реализацией. Флаги: `--quick` (мелкий фикс), `--issue N` (GitHub issue) |
| `/implement` | После одобрения плана, выполняет TDD workflow |
| `/review` | После реализации, перед merge |
| `/done` | После APPROVED ревью, архивирует задачу |

## Workflow

```
/plan → state.json → /implement → атомарные коммиты → /review → /done → merge
```

**TDD Цикл** (dev-agent):
1. Напиши тест (должен УПАСТЬ - RED)
2. Напиши минимум кода (тест ПРОХОДИТ - GREEN)
3. Рефактори
4. Закоммить
5. Обнови state.json

## Агенты

| Агент | Роль | Для чего |
|-------|------|----------|
| `dev-agent` | Разработчик | TDD реализация (тесты + код) |
| `review-agent` | Ревьюер | Независимая проверка кода |
| `explore-agent` | Разведчик | Быстрый поиск по коду (haiku) |
| `doc-agent` | Документатор | Документация |

## Ключевые файлы

- `.claude-workspace/state.json` - Единый файл состояния (план, прогресс, фичи, решения)
- `.claude-workspace/archive/` - Архив завершённых задач
- `.claude/settings.local.json` - Настройки permissions и hooks

## state.json структура

```json
{
  "project": "project-name",
  "currentTask": {
    "id": "F001",
    "name": "Feature name",
    "status": "planned|in_progress|review|done",
    "steps": [{"id": 1, "name": "...", "completed": false}]
  },
  "features": [{"id": "F001", "name": "...", "status": "done"}],
  "progress": [{"timestamp": "...", "type": "PLAN|IMPLEMENT|REVIEW|COMPLETE", "message": "..."}],
  "decisions": [{"id": "ADR-001", "title": "...", "decision": "..."}]
}
```

## Git-конвенции

Формат: `type(scope): description`

Типы: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

## Безопасность

### Автоматически разрешено
- Git: add, commit, checkout, pull, stash, rm
- Python: все команды
- Docker: stop, rm

### Требует подтверждения
- SSH подключения
- Docker exec/run

### Заблокировано (PreToolUse hook)
- rm -rf /, ~, *, .
- git reset --hard, push --force, clean -fd
- curl/wget | sh
- chmod 000/777
- mkfs, dd of=/dev
