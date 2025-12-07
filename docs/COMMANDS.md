# Slash Commands

Справочник по всем slash-командам Claude Code Kit.

## Обзор команд

| Команда | Описание | Когда использовать |
|---------|----------|-------------------|
| `/init-project` | Инициализация проекта | Один раз в начале |
| `/create-plan [feature]` | Планирование фичи | Перед реализацией > 50 LOC |
| `/implement` | Реализация по плану | После одобрения плана |
| `/code-review` | Код-ревью | После реализации |
| `/complete-task` | Завершение задачи | После APPROVED ревью |
| `/test [feature]` | Тестирование | После реализации |
| `/quick-fix [bug]` | Быстрый fix | Для мелких багов < 20 LOC |
| `/project-status` | Статус проекта | В любое время |
| `/fix-issue [#N]` | Fix GitHub issue | Когда есть issue |

---

## /init-project

**Файл:** `.claude/commands/init-project.md`

### Описание

Инициализирует проект для работы с Claude Code. Создаёт структуру директорий и файлы отслеживания.

### Когда использовать

- При начале работы с новым проектом
- После клонирования шаблона Claude Code Kit
- Один раз в начале проекта

### Аргументы

Нет

### Что делает

1. Анализирует тип проекта (Node.js, Python, Rust, Go)
2. Создаёт структуру директорий:
   - `.claude-workspace/`
   - `.claude/commands/`
   - `.claude/agents/`
3. Создаёт tracking файлы:
   - `progress.md`
   - `features.json`
   - `current-task.md`
   - `decisions.md`
4. Создаёт/обновляет `CLAUDE.md`
5. Настраивает `.gitignore`
6. Делает initial commit

### Пример использования

```
/init-project
```

### Связанные

- После: `/project-status`, `/create-plan`

---

## /create-plan

**Файл:** `.claude/commands/create-plan.md`

### Описание

Создаёт детальный план реализации фичи или задачи. НЕ пишет код.

### Когда использовать

- Перед реализацией любой фичи > 50 строк кода
- Когда пользователь говорит "create-plan", "design", "architect"
- Для сложных задач требующих декомпозиции

### Аргументы

```
/create-plan [описание фичи]
```

Примеры:
- `/create-plan user authentication`
- `/create-plan add dark mode toggle`
- `/create-plan refactor database layer`

### Что делает

1. **Explore** — изучает структуру проекта и существующий код
2. **Think** — отвечает на вопросы:
   - Какие файлы изменить?
   - Какие файлы создать?
   - Какие зависимости добавить?
   - Какие риски?
3. **Document** — записывает план в `current-task.md`:
   - Objective
   - Complexity (S/M/L/XL)
   - Implementation Steps
   - Files to Create/Modify
   - Success Criteria
   - Risks & Mitigations

### Пример использования

```
/create-plan implement JWT authentication

# Выход:
## Task: JWT Authentication

### Objective
Добавить JWT аутентификацию для защиты API endpoints.

### Complexity: M
### Estimated Steps: 5
### Risk Level: Medium

### Implementation Steps
1. [ ] Step 1: Add JWT dependencies
2. [ ] Step 2: Create auth middleware
...
```

### Связанные

- **Агент:** `lead-agent`
- **После:** `/implement`

---

## /implement

**Файл:** `.claude/commands/implement.md`

### Описание

Реализует задачу из `current-task.md` следуя TDD подходу.

### Когда использовать

- После одобрения плана (`/create-plan`)
- Когда есть готовый план в `current-task.md`

### Аргументы

Нет (работает с `current-task.md`)

### Что делает

1. **Pre-check:**
   - Проверяет наличие плана
   - Проверяет baseline (тесты проходят)
   - Показывает текущую задачу

2. **Для каждого шага плана:**
   - Write Test (RED) — тест должен упасть
   - Write Code (GREEN) — минимум для прохождения
   - Refactor — улучшение без изменения поведения
   - Commit — атомарный коммит
   - Update tracking — отметить шаг

3. **Post-check:**
   - Все тесты проходят
   - Linting без ошибок
   - Код компилируется

### Пример использования

```
/implement

# Процесс:
Step 1/5: Add JWT dependencies
- Writing test... FAIL (expected)
- Writing code...
- Running test... PASS
- Committing: "feat(auth): add JWT dependencies"

Step 2/5: Create auth middleware
...
```

### Связанные

- **Агент:** `code-agent`
- **До:** `/create-plan`
- **После:** `/code-review`

---

## /code-review

**Файл:** `.claude/commands/code-review.md`

### Описание

Проводит независимое код-ревью недавних изменений.

### Когда использовать

- После завершения реализации (`/implement`)
- Когда пользователь говорит "review", "check code"
- Перед merge в main ветку

### Аргументы

```
/code-review [scope]
```

Варианты scope:
- (пусто) — последние 5 коммитов (auto)
- `N` — последние N коммитов
- `staged` — только staged changes
- `branch` — все коммиты ветки относительно main
- `all` — uncommitted + последние 5 коммитов

### Что делает

1. **Understand Intent** — читает план из `current-task.md`
2. **Gather Changes** — собирает diff и статистику
3. **Automated Checks:**
   - Тесты
   - Linting
   - Type checking
4. **Security Scan:**
   - Secrets detection
   - SQL/Command injection
   - Console.log в production
5. **Deep Review** — проверяет каждый файл

### Auto-REJECT критерии

| Finding | Severity | Action |
|---------|----------|--------|
| Hardcoded secrets | CRITICAL | REJECT |
| SQL/Command injection | CRITICAL | REJECT |
| console.log в production | HIGH | CHANGES REQUESTED |
| Missing tests | HIGH | CHANGES REQUESTED |
| Coverage decreased | HIGH | CHANGES REQUESTED |

### Пример использования

```
/code-review

# или
/code-review 3        # последние 3 коммита
/code-review staged   # только staged
/code-review branch   # вся ветка
```

### Формат вывода

```markdown
## Code Review Summary

**Status:** APPROVED / CHANGES REQUESTED / REJECTED
**Quality Score:** 4/5

### Findings
#### Critical (must fix)
...

### What's Good
- ...

### Before Merge Checklist
- [ ] All findings addressed
- [ ] Tests pass
```

### Связанные

- **Агент:** `review-agent`
- **До:** `/implement`
- **После:** `/complete-task` (если APPROVED) или fix → `/code-review staged`

---

## /complete-task

**Файл:** `.claude/commands/complete-task.md`

### Описание

Завершает текущую задачу: архивирует план, обновляет features.json, очищает workspace для следующей задачи.

### Когда использовать

- После получения APPROVED вердикта от `/code-review`
- Когда задача полностью завершена и готова к merge
- Перед началом работы над новой задачей

### Аргументы

Нет (работает с `current-task.md`)

### Что делает

1. **Валидация:**
   - Проверяет наличие задачи в `current-task.md`
   - Проверяет что все шаги отмечены как выполненные

2. **Архивация:**
   - Копирует `current-task.md` → `archive/YYYY-MM-DD-slug.md`
   - Сохраняет полный план для истории

3. **Обновление tracking:**
   - Обновляет `features.json`: status → "done", completedAt, archivePath
   - Добавляет запись [COMPLETED] в `progress.md`

4. **Очистка:**
   - Сбрасывает `current-task.md` на шаблон "No active task"

### Пример использования

```
/complete-task

# Выход:
## Task Completed

**Task:** JWT Authentication
**Duration:** 2h 30m
**Archived to:** archive/2024-01-15-jwt-authentication.md

### Summary
- 5 steps completed
- 12 commits made
- 3 files created, 2 modified

### features.json Updated
- Status: done
- Completed at: 2024-01-15T14:30:00Z

Ready for next task. Run `/create-plan [feature]` to start.
```

### Связанные

- **До:** `/code-review` (APPROVED)
- **После:** `/create-plan [next-feature]`

---

## /test

**Файл:** `.claude/commands/test.md`

### Описание

Проводит комплексное тестирование фичи как реальный пользователь.

### Когда использовать

- После реализации для верификации
- Когда нужно E2E тестирование
- Для проверки конкретной функциональности

### Аргументы

```
/test [feature]
```

### Что делает

1. **Setup:**
   - Запускает dev server (если нужно)
   - Определяет test framework
   - Находит существующие тесты

2. **Testing:**
   - Unit тесты
   - Integration тесты
   - E2E тесты (с browser automation или API)

3. **Scenarios Matrix:**
   - Happy path
   - Empty input
   - Invalid input
   - Boundary cases
   - Special characters
   - Concurrent access
   - Network errors

4. **Coverage Check**

### Пример использования

```
/test authentication

# Выход:
## Test Results: authentication

### Summary
| Type | Total | Pass | Fail |
|------|-------|------|------|
| Unit | 15 | 14 | 1 |
| E2E | 3 | 3 | 0 |

### Failed Tests
1. `test_invalid_token`
   - Expected: 401
   - Actual: 500

### Bugs Found
1. [HIGH] Token expiration not handled
```

### Связанные

- **Агент:** `test-agent`
- **До:** `/implement` или `/code-review`

---

## /quick-fix

**Файл:** `.claude/commands/quick-fix.md`

### Описание

Быстрое исправление небольшого бага БЕЗ полного цикла планирования.

### Когда использовать

- Изменения < 20 строк кода
- Очевидный баг с понятным fix
- НЕ новая функциональность
- НЕ рефакторинг

### Аргументы

```
/quick-fix [описание бага]
```

### Что делает

1. **Find** — поиск проблемы по описанию
2. **Read** — изучение файла с багом
3. **Test** — написание теста (должен упасть)
4. **Fix** — минимальные изменения
5. **Verify** — тест проходит, остальные тоже
6. **Commit** — `fix(scope): description`

### Constraints

Если fix сложнее чем ожидалось — команда останавливается и рекомендует `/create-plan`.

### Пример использования

```
/quick-fix email validation broken

# Выход:
## Quick Fix Complete: email validation broken

### Problem
Email regex не принимал домены с цифрами.

### Solution
Обновлён regex pattern в validators.ts:42

### Changes
- `src/validators.ts:42` — updated regex

### Test Added
- `test_email_with_numbers_in_domain`
```

### Связанные

- **Альтернатива:** `/create-plan` (для сложных фиксов)

---

## /project-status

**Файл:** `.claude/commands/project-status.md`

### Описание

Показывает текущий статус проекта.

### Когда использовать

- В начале сессии
- Когда пользователь спрашивает "what's next", "where are we"
- Для быстрой ориентации

### Аргументы

```
/project-status [mode]
```

Варианты mode:
- (пусто) — полный статус
- `compact` или `short` — краткий вывод

### Что показывает

**Compact mode:**
```markdown
## Status (compact)

**Task:** Feature X
**Progress:** 3/5 steps
**Branch:** `feature/x`
**Changes:** 2 uncommitted
**Tests:** OK

**Next:** Continue with step 4
```

**Full mode:**
- Current Task (из `current-task.md`)
- Recent Activity (из `progress.md`)
- Features Overview (из `features.json`)
- Git Status (branch, changes, commits)
- Tests (pass/fail, coverage)
- Warnings (blockers, issues)
- Recommended Next Steps

### Пример использования

```
/project-status

# или
/project-status compact
```

### Связанные

- **После:** рекомендует релевантную команду

---

## /fix-issue

**Файл:** `.claude/commands/fix-issue.md`

### Описание

Анализирует и исправляет GitHub issue по номеру.

### Когда использовать

- Когда есть конкретный GitHub issue
- Когда пользователь упоминает номер issue

### Prerequisites

- GitHub CLI (`gh`) установлен
- Авторизация в GitHub (`gh auth login`)

### Аргументы

```
/fix-issue [номер]
```

### Что делает

1. **Get Issue** — получает детали issue через `gh`
2. **Investigate:**
   - Поиск в codebase по ключевым словам
   - Проверка связанных PRs
   - Git history
3. **Reproduce** — попытка воспроизвести локально
4. **Plan** — записывает план в `current-task.md`
5. **Implement (TDD):**
   - Создаёт ветку `fix/issue-N`
   - Пишет тест воспроизводящий баг
   - Исправляет код
   - Верифицирует
6. **PR:**
   - Коммит с `Fixes #N`
   - Push ветки
   - Создание PR через `gh pr create`
7. **Update Tracking**

### Пример использования

```
/fix-issue 42

# Выход:
## Issue #42 Fixed

### Issue
**Title:** Login button not working on mobile
**Labels:** bug, mobile

### Root Cause
Touch event handler не был привязан.

### Solution
Добавлен onTouchStart handler.

### PR
**Branch:** `fix/issue-42`
**PR:** https://github.com/repo/pull/123
```

### Error Handling

- Issue not found → сообщение с рекомендациями
- Cannot reproduce → документирует попытки, предлагает варианты

### Связанные

- **Альтернатива:** `/quick-fix` (без GitHub integration)
- **Требует:** GitHub CLI (`gh`)

---

## Выбор команды

```
                    ┌─────────────────────┐
                    │   Какая задача?     │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           v                   v                   v
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ Новый проект │   │  Новая фича  │   │  Баг/Issue   │
    └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                   │                   │
           v                   v                   v
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ /init-project│   │  > 50 LOC?   │   │ GitHub issue?│
    └──────────────┘   └──────┬───────┘   └──────┬───────┘
                              │                   │
                    ┌─────────┴─────────┐   ┌─────┴─────┐
                    │                   │   │           │
                    v                   v   v           v
             ┌──────────┐         ┌──────────┐   ┌──────────┐
             │/create-  │         │/implement│   │/fix-issue│
             │  plan    │         │ напрямую │   └──────────┘
             └────┬─────┘         └──────────┘
                  │               └──────────┘
                  v                              ┌──────────┐
             ┌──────────┐                        │< 20 LOC? │
             │/implement│                        └────┬─────┘
             └────┬─────┘                             │
                  │                         ┌────────┴────────┐
                  v                         v                 v
             ┌──────────┐            ┌──────────┐      ┌──────────┐
             │/code-    │            │/quick-fix│      │/create-plan│
             └──────────┘            └──────────┘      └──────────┘
```
