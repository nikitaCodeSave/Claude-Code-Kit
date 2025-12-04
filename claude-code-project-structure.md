# Claude Code Project Structure
## Основано на рекомендациях Anthropic

Структура проекта для эффективной работы с Claude Code, объединяющая:
- Long-running agents паттерны
- Multi-agent research system
- Claude Code best practices

---

## 📁 Структура файлов проекта

```
project-root/
├── CLAUDE.md                      # Основной контекст проекта
├── CLAUDE.local.md                # Локальные настройки (git-ignored)
├── .mcp.json                      # MCP серверы для команды
│
├── .claude/
│   ├── settings.json              # Настройки Claude Code
│   ├── settings.local.json        # Локальные настройки
│   │
│   └── commands/                  # Slash commands
│       ├── init-project.md        # /project:init-project
│       ├── plan.md                # /project:plan
│       ├── implement.md           # /project:implement
│       ├── review.md              # /project:review
│       ├── test.md                # /project:test
│       ├── fix-issue.md           # /project:fix-issue
│       └── status.md              # /project:status
│
├── .claude-workspace/             # Рабочие файлы агентов
│   ├── progress.md                # Лог прогресса (как в long-running agents)
│   ├── features.json              # Список фич со статусами
│   ├── current-task.md            # Текущая задача
│   └── decisions.md               # Архитектурные решения
│
└── docs/
    └── agents/                    # Промпты агентов
        ├── lead-agent.md
        ├── code-agent.md
        ├── review-agent.md
        └── test-agent.md
```

---

## 📄 CLAUDE.md (Основной файл)

```markdown
# Project: [PROJECT_NAME]

## Overview
[Краткое описание проекта в 2-3 предложения]

## Tech Stack
- Language: [Python 3.11 / TypeScript 5.x / etc.]
- Framework: [FastAPI / Next.js / etc.]
- Database: [PostgreSQL / Qdrant / etc.]
- Testing: [pytest / vitest / etc.]

## Commands
- `npm run dev` / `python -m uvicorn main:app --reload` - Dev server
- `npm run build` / `python -m build` - Build
- `npm run test` / `pytest` - Run tests
- `npm run lint` / `ruff check .` - Linting

## Code Style
- IMPORTANT: Use ES modules (import/export), not CommonJS
- IMPORTANT: Type hints required for all functions
- Prefer composition over inheritance
- Max function length: 50 lines
- YOU MUST run typecheck after code changes

## Project Structure
- `src/` - Main source code
- `tests/` - Test files (mirror src/ structure)
- `docs/` - Documentation
- `.claude-workspace/` - Claude working files

## Workflow Rules
1. ALWAYS read `.claude-workspace/progress.md` at session start
2. ALWAYS update progress.md after completing work
3. Work on ONE feature at a time
4. Commit after each completed feature with descriptive message
5. Run tests before marking feature as done

## Git Conventions
- Branch naming: `feature/`, `fix/`, `refactor/`
- Commit format: `type(scope): description`
- Always rebase, never merge to feature branches

## Known Issues
- [Список известных проблем и workarounds]

## Do Not
- Do NOT edit files in `legacy/` directory
- Do NOT commit directly to main branch
- Do NOT skip tests
- Do NOT remove items from features.json
```

---

## 🤖 Agents (Промпты для docs/agents/)

### 1. Lead Agent (Orchestrator)
**Файл:** `docs/agents/lead-agent.md`

```markdown
# Lead Agent - Orchestrator

## Role
Ты Lead Agent, отвечающий за планирование и координацию работы над проектом.
Ты анализируешь задачи, декомпозируешь их, и создаёшь детальные планы.

## Responsibilities
1. Анализ requirements и user stories
2. Декомпозиция на подзадачи
3. Определение приоритетов
4. Создание детальных планов реализации
5. Оценка рисков и зависимостей

## Process (OODA Loop)
1. **Observe**: Изучи текущее состояние проекта
   - Прочитай `.claude-workspace/progress.md`
   - Проверь `.claude-workspace/features.json`
   - Изучи git log последних коммитов
   
2. **Orient**: Оцени ситуацию
   - Что уже сделано?
   - Какие блокеры есть?
   - Какие ресурсы доступны?
   
3. **Decide**: Составь план
   - Выбери следующую фичу из features.json
   - Разбей на конкретные шаги
   - Определи критерии успеха
   
4. **Act**: Задокументируй план
   - Запиши в `.claude-workspace/current-task.md`
   - Обнови progress.md

## Scaling Rules
| Complexity | Subagents | Tool Calls per Agent |
|------------|-----------|---------------------|
| Simple (1 file) | 0 | 3-10 |
| Medium (2-5 files) | 1-2 | 10-15 |
| Complex (system-wide) | 3-5 | 15-25 |

## Output Format
План должен содержать:
1. Objective - чёткая цель
2. Scope - что входит и НЕ входит
3. Steps - пронумерованные шаги
4. Success Criteria - как проверить готовность
5. Risks - потенциальные проблемы

## Triggers
- Используй "think hard" для сложного планирования
- Используй "ultrathink" для архитектурных решений
```

### 2. Code Agent (Implementer)
**Файл:** `docs/agents/code-agent.md`

```markdown
# Code Agent - Implementer

## Role
Ты Code Agent, отвечающий за реализацию кода согласно плану.
Работаешь инкрементально, оставляя код в чистом состоянии.

## Responsibilities
1. Реализация фич согласно плану
2. Написание чистого, документированного кода
3. Следование code style проекта
4. Инкрементальные коммиты

## Process
1. **Start Session**:
   ```bash
   pwd  # Проверь рабочую директорию
   cat .claude-workspace/current-task.md  # Текущая задача
   cat .claude-workspace/progress.md  # Контекст
   git log --oneline -10  # Недавние изменения
   ```

2. **Before Coding**:
   - Убедись что dev server запускается
   - Проверь что базовый функционал работает
   - Если что-то сломано - СНАЧАЛА почини

3. **Implementation**:
   - Работай над ОДНОЙ фичей
   - Пиши тесты ПЕРЕД кодом (TDD)
   - Проверяй работу после каждого изменения

4. **After Coding**:
   - Запусти все тесты
   - Запусти linter
   - Сделай коммит с описательным сообщением
   - Обнови progress.md

## Clean State Checklist
Перед завершением сессии убедись:
- [ ] Все тесты проходят
- [ ] Нет linting ошибок
- [ ] Код закоммичен
- [ ] progress.md обновлён
- [ ] features.json обновлён (если фича готова)

## Rules
- НИКОГДА не оставляй код в сломанном состоянии
- НИКОГДА не удаляй тесты чтобы они "прошли"
- ВСЕГДА проверяй работу end-to-end
- Один коммит = одно логическое изменение
```

### 3. Review Agent (Verifier)
**Файл:** `docs/agents/review-agent.md`

```markdown
# Review Agent - Verifier

## Role
Ты Review Agent, независимо проверяющий качество кода.
Работаешь с ОТДЕЛЬНЫМ контекстом от Code Agent.

## Responsibilities
1. Code review на соответствие стандартам
2. Проверка логики и edge cases
3. Верификация что реализация соответствует плану
4. Выявление потенциальных багов

## Process
1. Прочитай план в `.claude-workspace/current-task.md`
2. Изучи изменения: `git diff HEAD~5`
3. Проверь каждый изменённый файл
4. Запиши findings

## Review Checklist
### Correctness
- [ ] Логика соответствует requirements
- [ ] Обработаны edge cases
- [ ] Нет очевидных багов

### Code Quality
- [ ] Следует code style проекта
- [ ] Нет дублирования кода
- [ ] Функции не слишком длинные
- [ ] Понятные имена переменных

### Safety
- [ ] Нет hardcoded credentials
- [ ] Input validation присутствует
- [ ] Ошибки обрабатываются корректно

### Testing
- [ ] Тесты покрывают основные сценарии
- [ ] Тесты покрывают edge cases
- [ ] Тесты не overfitted к реализации

## Output Format
```markdown
## Review Summary

### ✅ Approved / ⚠️ Changes Requested / ❌ Rejected

### Findings
1. [CRITICAL/MAJOR/MINOR] Description
   - File: path/to/file.py:line
   - Issue: what's wrong
   - Suggestion: how to fix

### Recommendations
- ...
```
```

### 4. Test Agent (QA)
**Файл:** `docs/agents/test-agent.md`

```markdown
# Test Agent - QA

## Role
Ты Test Agent, отвечающий за качество через тестирование.
Пишешь тесты ДО реализации (TDD) и верифицируешь end-to-end.

## Responsibilities
1. Написание unit тестов
2. Написание integration тестов
3. End-to-end тестирование (через Puppeteer/browser)
4. Верификация фич как реальный пользователь

## TDD Process
1. Получи requirements/plan
2. Напиши тесты на expected behavior
3. Запусти тесты - они ДОЛЖНЫ падать
4. Передай Code Agent для реализации
5. После реализации - тесты должны проходить

## E2E Testing Process
1. Запусти dev server
2. Используй browser automation (Puppeteer MCP)
3. Тестируй как реальный пользователь:
   - Открой страницу
   - Выполни действия
   - Проверь результат визуально
4. Сделай скриншоты для документации

## Test Quality Rules
- Тесты должны быть НЕЗАВИСИМЫ друг от друга
- Используй fixtures, не hardcoded data
- Тестируй behavior, не implementation
- Один тест = один сценарий

## Known Limitations
- Puppeteer MCP не видит browser-native alert modals
- Некоторые CSS анимации могут влиять на timing
- Учитывай async операции с правильными waits
```

---

## ⚡ Slash Commands

### /project:init-project
**Файл:** `.claude/commands/init-project.md`

```markdown
# Initialize Project for Claude Code

Инициализируй проект для эффективной работы с Claude Code.

## Steps
1. Создай структуру `.claude-workspace/`:
   - progress.md - пустой лог прогресса
   - features.json - пустой список фич
   - current-task.md - placeholder
   - decisions.md - архитектурные решения

2. Если CLAUDE.md не существует:
   - Проанализируй проект
   - Создай CLAUDE.md с tech stack, commands, code style
   
3. Проверь/создай `.claude/commands/` с базовыми командами

4. Сделай начальный коммит workspace файлов

5. Выведи summary что создано

## Output
Покажи созданную структуру и следующие шаги.
```

### /project:plan
**Файл:** `.claude/commands/plan.md`

```markdown
# Plan Feature/Task: $ARGUMENTS

Создай детальный план для задачи. НЕ ПИШИ КОД.

## Process
1. **Explore** (используй subagents для сложных задач):
   - Изучи релевантные файлы проекта
   - Проверь существующие паттерны
   - Найди похожие реализации в codebase

2. **Think Hard** о подходе:
   - Какие файлы нужно изменить?
   - Какие новые файлы создать?
   - Какие зависимости добавить?
   - Какие риски есть?

3. **Document Plan**:
   - Запиши план в `.claude-workspace/current-task.md`
   - Обнови `.claude-workspace/progress.md`
   - Если новая фича - добавь в `features.json`

## Output Format
```markdown
## Task: [название]

### Objective
[Чёткая цель в 1-2 предложения]

### Scope
**In Scope:**
- ...

**Out of Scope:**
- ...

### Implementation Steps
1. [ ] Step 1 - description
2. [ ] Step 2 - description
...

### Files to Modify
- `path/to/file.py` - reason
- ...

### Files to Create
- `path/to/new.py` - purpose
- ...

### Dependencies
- [если нужны новые пакеты]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Risks
- Risk 1 - mitigation
```

## Important
- Используй "think hard" или "ultrathink" для сложных задач
- НЕ начинай писать код пока план не одобрен
- Спроси подтверждение перед переходом к реализации
```

### /project:implement
**Файл:** `.claude/commands/implement.md`

```markdown
# Implement Current Task

Реализуй задачу из `.claude-workspace/current-task.md`.

## Pre-Implementation Checklist
1. Прочитай current-task.md
2. Убедись что план одобрен
3. Проверь что dev environment работает:
   ```bash
   # Запусти dev server
   # Проверь базовый функционал
   ```

## Implementation Process
1. **Для каждого шага из плана:**
   - Напиши тесты СНАЧАЛА (TDD)
   - Запусти тесты - они должны падать
   - Напиши минимальный код для прохождения
   - Рефактори если нужно
   - Закоммить с описательным сообщением

2. **После каждого коммита:**
   - Обнови progress.md
   - Отметь выполненные шаги в current-task.md

3. **После завершения всех шагов:**
   - Запусти ВСЕ тесты
   - Запусти linter
   - Если фича готова - обнови features.json

## Rules
- Работай над ОДНИМ шагом за раз
- НЕ пропускай тесты
- Коммить ЧАСТО (после каждого логического изменения)
- Если что-то сломалось - почини СРАЗУ

## Output
После завершения покажи:
- Список созданных/изменённых файлов
- Результаты тестов
- Git log последних коммитов
```

### /project:review
**Файл:** `.claude/commands/review.md`

```markdown
# Review Recent Changes

Проведи code review недавних изменений как НЕЗАВИСИМЫЙ Review Agent.

## Process
1. Очисти контекст от предыдущей работы (мысленно)
2. Прочитай план в current-task.md
3. Изучи изменения:
   ```bash
   git diff HEAD~$ARGUMENTS  # default: 5
   git log --oneline -$ARGUMENTS
   ```
4. Для каждого изменённого файла проверь:
   - Соответствие плану
   - Code quality
   - Edge cases
   - Security

## Review Checklist
### Correctness
- [ ] Реализация соответствует requirements
- [ ] Edge cases обработаны
- [ ] Ошибки handled gracefully

### Quality
- [ ] Следует code style из CLAUDE.md
- [ ] Нет code duplication
- [ ] Понятные имена
- [ ] Достаточная документация

### Testing
- [ ] Тесты существуют
- [ ] Тесты покрывают main scenarios
- [ ] Тесты не overfitted

### Security
- [ ] No hardcoded secrets
- [ ] Input validation
- [ ] Proper error handling

## Output
```markdown
## Code Review Summary

**Status:** ✅ Approved / ⚠️ Changes Requested / ❌ Needs Rework

### Findings
[Numbered list of issues with severity]

### Recommendations
[Suggestions for improvement]

### Next Steps
[What should happen next]
```
```

### /project:test
**Файл:** `.claude/commands/test.md`

```markdown
# Test Feature: $ARGUMENTS

Протестируй фичу end-to-end как реальный пользователь.

## Process
1. Запусти dev server если не запущен
2. Если есть Puppeteer MCP:
   - Открой приложение в браузере
   - Выполни user flow
   - Сделай скриншоты ключевых шагов
3. Если нет browser automation:
   - Используй curl/httpie для API
   - Проверь responses
4. Запусти unit/integration тесты
5. Задокументируй результаты

## Test Scenarios
Для фичи "$ARGUMENTS" проверь:
1. **Happy Path** - основной сценарий работает
2. **Edge Cases** - граничные случаи
3. **Error Cases** - ошибки обрабатываются
4. **Performance** - нет очевидных проблем

## Output
```markdown
## Test Results: $ARGUMENTS

**Status:** ✅ Pass / ⚠️ Partial / ❌ Fail

### Scenarios Tested
1. [Scenario] - ✅/❌ - notes
2. ...

### Screenshots
[Если доступны]

### Issues Found
- [Issue 1]
- ...

### Recommendations
- ...
```

## Important
- Тестируй как РЕАЛЬНЫЙ пользователь
- Не полагайся только на unit тесты
- Проверяй визуально если возможно
```

### /project:fix-issue
**Файл:** `.claude/commands/fix-issue.md`

```markdown
# Fix GitHub Issue: $ARGUMENTS

Проанализируй и исправь GitHub issue #$ARGUMENTS.

## Process
1. **Получи детали issue:**
   ```bash
   gh issue view $ARGUMENTS
   ```

2. **Explore** проблему:
   - Найди релевантные файлы
   - Воспроизведи проблему если возможно
   - Изучи контекст

3. **Plan** исправление:
   - Определи root cause
   - Спланируй fix
   - Запиши в current-task.md

4. **Implement** fix:
   - Напиши тест воспроизводящий баг
   - Исправь код
   - Убедись что тест проходит

5. **Verify:**
   - Запусти все тесты
   - Проверь что fix не сломал другое

6. **Complete:**
   - Закоммить с сообщением "fix(scope): description. Fixes #$ARGUMENTS"
   - Создай PR

## Output
После завершения:
- Summary что было исправлено
- Ссылка на PR
- Обнови progress.md
```

### /project:status
**Файл:** `.claude/commands/status.md`

```markdown
# Project Status

Покажи текущий статус проекта.

## Gather Information
1. Прочитай `.claude-workspace/progress.md`
2. Прочитай `.claude-workspace/features.json`
3. Проверь git status
4. Посмотри последние коммиты

## Output Format
```markdown
## Project Status

### Current Task
[Из current-task.md или "No active task"]

### Recent Progress
[Последние 5 записей из progress.md]

### Features Status
- ✅ Completed: X
- 🔄 In Progress: Y
- ⏳ Pending: Z

### Git Status
- Branch: [current branch]
- Uncommitted changes: [yes/no]
- Last commit: [message]

### Next Steps
1. [Recommendation 1]
2. [Recommendation 2]
```
```

---

## 📊 Workspace Files

### .claude-workspace/progress.md
```markdown
# Progress Log

## Session: [DATE TIME]
- **Task:** [что делалось]
- **Completed:** [что завершено]
- **Commits:** [список коммитов]
- **Notes:** [заметки для следующей сессии]

---

[Предыдущие сессии...]
```

### .claude-workspace/features.json
```json
{
  "features": [
    {
      "id": "F001",
      "name": "User Authentication",
      "description": "Login/logout with JWT tokens",
      "priority": 1,
      "status": "done",
      "completedAt": "2025-01-15"
    },
    {
      "id": "F002", 
      "name": "Dashboard API",
      "description": "REST endpoints for dashboard data",
      "priority": 2,
      "status": "in_progress",
      "steps": [
        {"name": "GET /api/stats", "done": true},
        {"name": "GET /api/charts", "done": false},
        {"name": "Tests", "done": false}
      ]
    },
    {
      "id": "F003",
      "name": "Export to PDF",
      "description": "Generate PDF reports",
      "priority": 3,
      "status": "pending"
    }
  ]
}
```

### .claude-workspace/current-task.md
```markdown
# Current Task: [Feature Name]

## Objective
[Clear goal]

## Plan
1. [ ] Step 1
2. [ ] Step 2
3. [ ] Step 3

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Notes
[Any relevant notes]
```

---

## 🔧 .mcp.json (Team Configuration)

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-puppeteer"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "--root", "."]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## 🚀 Quick Start

```bash
# 1. Инициализируй проект
claude
> /project:init-project

# 2. Создай план для первой фичи
> /project:plan User authentication with JWT

# 3. После одобрения плана - реализуй
> /project:implement

# 4. Review кода
> /project:review 5

# 5. Тестирование
> /project:test authentication

# 6. Статус проекта
> /project:status
```

---

## 💡 Best Practices Summary

1. **Всегда начинай с Explore → Plan**
   - Используй "think hard" / "ultrathink" на этапе планирования
   - Opus 4.5 для планирования, Sonnet 4.5 для реализации

2. **Один feature за раз**
   - Не пытайся сделать всё сразу
   - Коммить после каждого логического изменения

3. **Progress tracking**
   - Обновляй progress.md в конце КАЖДОЙ сессии
   - Это твоя память между context windows

4. **TDD workflow**
   - Тесты → Код → Refactor
   - Независимая верификация через Review Agent

5. **Clean state**
   - Никогда не оставляй код сломанным
   - Следующая сессия должна стартовать с working state
