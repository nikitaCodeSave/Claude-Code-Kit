# CLAUDE.md

Этот файл содержит инструкции для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Обзор

Claude Code Kit — шаблонный проект со структурой, агентами и slash-командами для работы с Claude Code. Копируйте и адаптируйте под свои проекты.

## Правила сессии

1. **НАЧАЛО**: Прочитай `.claude-workspace/progress.md` для контекста
2. **КОНЕЦ**: Обнови `progress.md` с результатами работы
3. Работай над ОДНОЙ фичей за раз
4. Используй `/plan` для фич > 50 строк кода
5. Используй `/review` после реализации

## Команды

| Команда | Когда использовать |
|---------|-------------------|
| `/plan [feature]` | Перед реализацией фич > 50 строк кода |
| `/implement` | После одобрения плана, выполняет TDD workflow |
| `/review` | После реализации, перед merge |
| `/test [feature]` | E2E тестирование готовых фич |
| `/quick-fix [bug]` | Только для мелких багов < 20 строк |
| `/project-status` | Проверить текущее состояние и следующие шаги |
| `/init-project` | Инициализация нового проекта (один раз) |
| `/fix-issue [#N]` | Исправление GitHub issue по номеру |

## Workflow

```
/plan → current-task.md → /implement → атомарные коммиты → /review → merge
```

**TDD Цикл** (контролируется code-agent):
1. Напиши тест (должен УПАСТЬ)
2. Напиши минимум кода (тест ПРОХОДИТ)
3. Рефактори
4. Закоммить

## Агенты

| Агент | Роль | Для чего |
|-------|------|----------|
| `lead-agent` | Архитектор | Планирование, декомпозиция |
| `code-agent` | Разработчик | TDD реализация |
| `review-agent` | Ревьюер | Независимая проверка кода |
| `test-agent` | QA | Тестирование, поиск багов |
| `explore-agent` | Разведчик | Быстрый поиск по коду |
| `doc-agent` | Документатор | Документация |

## Ключевые файлы

- `.claude-workspace/progress.md` - Память между сессиями (читай первым!)
- `.claude-workspace/current-task.md` - План текущей задачи
- `.claude-workspace/decisions.md` - Лог архитектурных решений
- `.claude-workspace/features.json` - Отслеживание фич и их статусов
- `.claude/settings.local.json` - Настройки permissions и hooks

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

## Документация

Подробная документация в `docs/`:
- `docs/README.md` — общее описание
- `docs/WORKFLOW.md` — workflow и процессы
- `docs/COMMANDS.md` — справка по командам
- `docs/AGENTS.md` — справка по агентам
