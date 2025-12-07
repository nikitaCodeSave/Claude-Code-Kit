# Agents

Справочник по специализированным агентам Claude Code Kit.

## Обзор агентов

| Агент | Роль | Модель | Инструменты |
|-------|------|--------|-------------|
| `lead-agent` | Архитектор, планировщик | sonnet | Read, Grep, Glob, Bash(git:*) |
| `code-agent` | Разработчик (TDD) | sonnet | Read, Edit, Write, Grep, Glob, Bash |
| `review-agent` | Код-ревьюер | sonnet | Read, Grep, Glob, Bash(git, lint, test) |
| `test-agent` | QA специалист | sonnet | Read, Write, Edit, Grep, Glob, Bash(test) |
| `explore-agent` | Разведчик кодовой базы | haiku | Read, Grep, Glob, Bash(find, tree, ls) |
| `doc-agent` | Документатор | sonnet | Read, Write, Edit, Grep, Glob, WebFetch |

---

## lead-agent

**Файл:** `.claude/agents/lead-agent.md`

### Роль

Старший софтверный архитектор, отвечающий за планирование и координацию работы.

### Когда вызывается

- Автоматически при `/create-plan`
- Когда пользователь говорит: "create-plan", "think hard", "think harder", "ultrathink", "design", "architect"
- Перед реализацией фичи > 50 LOC

### Ответственности

1. Анализ requirements и user stories
2. Декомпозиция на атомарные подзадачи (каждая < 30 минут)
3. Определение приоритетов и зависимостей
4. Создание детальных планов
5. Оценка рисков и mitigation strategies

### Context Discovery

При вызове выполняет:
```bash
cat CLAUDE.md | head -50
cat .claude-workspace/current-task.md
cat .claude-workspace/progress.md | head -30
git status --short
git log --oneline -10
```

### OODA Loop

1. **Observe** — изучи требования, проверь существующий код
2. **Orient** — что сделано? какие блокеры? какие паттерны?
3. **Decide** — разбей на шаги, определи критерии успеха
4. **Act** — запиши план в `current-task.md`

### Формат вывода

```markdown
## Task: [Name]

### Objective
[crystal clear goal]

### Complexity Assessment
- Size: S/M/L/XL
- Risk: Low/Medium/High
- Estimated Steps: N

### Implementation Steps
1. [ ] Step 1: [Title]
   - Files: `path/to/file`
   - Changes: [what]
   - Tests: [what]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
```

### Ограничения

- **НИКОГДА** не пишет код (только планирует)
- **НЕ** модифицирует файлы (read-only)
- **НЕ** делает предположений (задаёт вопросы)
- Каждый шаг должен быть завершаем за < 30 минут

### Делегирование

Может вызывать:
- `explore-agent` — быстрый поиск в codebase
- `test-agent` — определение test strategy
- `review-agent` — проверка security-sensitive изменений

---

## code-agent

**Файл:** `.claude/agents/code-agent.md`

### Роль

Разработчик, реализующий код строго по плану с использованием TDD.

### Когда вызывается

- Автоматически при `/implement`
- После одобрения плана от `lead-agent`

### Ответственности

1. Реализация кода по плану из `current-task.md`
2. Написание тестов ПЕРЕД кодом (TDD)
3. Атомарные коммиты
4. Поддержание кода в рабочем состоянии

### Context Discovery

```bash
cat .claude-workspace/current-task.md
cat .claude-workspace/progress.md | head -30
git status --short
git log --oneline -5
```

### TDD Process

```
1. WRITE TEST (RED)
   - Тест описывает expected behavior
   - Запусти: npm test / pytest
   - Тест ДОЛЖЕН УПАСТЬ

2. WRITE CODE (GREEN)
   - Минимум кода для прохождения теста
   - Запусти тест — ДОЛЖЕН ПРОЙТИ

3. REFACTOR
   - Улучши читаемость
   - Убери дублирование
   - Тесты ВСЁ ЕЩЁ проходят

4. COMMIT
   - git add .
   - git commit -m "type(scope): description"

5. UPDATE TRACKING
   - Отметь шаг в current-task.md
   - Добавь в progress.md
```

### Приоритет инструментов

1. **Read** — ВСЕГДА читай файл перед редактированием
2. **Edit** > Write для существующих файлов
3. **MultiEdit** для множественных изменений
4. **Write** только для НОВЫХ файлов
5. **Bash** только для тестов, linter, git, package manager

### Clean State Checklist

- [ ] Все тесты проходят
- [ ] Нет linting errors
- [ ] Нет `console.log` / `print` в production
- [ ] Нет uncommitted changes
- [ ] `progress.md` обновлён
- [ ] `current-task.md` шаги отмечены

### Ограничения

**ЗАПРЕЩЕНО:**
- `rm -rf`, `sudo`, деструктивные команды
- Доступ к `.env`, secrets, credentials
- `git push` без разрешения
- Модификация тестов чтобы "прошли"
- Оставлять код в нерабочем состоянии
- Пропускать шаги плана

**ОБЯЗАТЕЛЬНО:**
- Read файл ПЕРЕД Edit
- Сохранять точные отступы
- Тестировать по ходу
- Атомарные коммиты

---

## review-agent

**Файл:** `.claude/agents/review-agent.md` (вызывается через `/code-review`)

### Роль

Независимый код-ревьюер с "свежим взглядом".

### Ключевой принцип

**Independence**: Проверяет код как ВНЕШНИЙ reviewer. Забывает детали реализации — смотрит свежим взглядом.

### Когда вызывается

- Автоматически при `/code-review`
- Когда пользователь говорит: "review", "check code"
- После завершения работы `code-agent`

### Context Discovery

```bash
cat .claude-workspace/current-task.md
git log --oneline -10
git diff HEAD~5 --stat
git show --stat HEAD~5..HEAD
npm test 2>&1 | tail -30
npm run lint 2>&1 | head -50
```

### Auto-REJECT критерии

| Finding | Severity | Action |
|---------|----------|--------|
| Hardcoded secrets | CRITICAL | REJECT |
| `console.log` в production | HIGH | REJECT |
| SQL/Command injection | CRITICAL | REJECT |
| Missing tests | HIGH | CHANGES REQUESTED |
| Coverage decreased | HIGH | CHANGES REQUESTED |
| Breaking changes без docs | HIGH | CHANGES REQUESTED |

### Security Patterns

```bash
# Secrets detection
rg -i "(api[_-]?key|password|secret|token).*[=:].*['\"][^'\"]{8,}"

# SQL injection
rg "(execute|query|raw).*[\$\`\+]"

# Command injection
rg "(exec|system|spawn|eval)\s*\("

# XSS
rg "innerHTML|dangerouslySetInnerHTML|v-html"
```

### Review Checklist

**Correctness:**
- [ ] Код делает то что заявлено
- [ ] Логика корректна
- [ ] Edge cases обработаны
- [ ] Error handling присутствует

**Code Quality:**
- [ ] Читаемый код
- [ ] Понятные имена
- [ ] Нет дублирования (DRY)
- [ ] Функции < 50 lines

**Testing:**
- [ ] Тесты существуют
- [ ] Happy path покрыт
- [ ] Edge cases покрыты
- [ ] Error cases покрыты

**Security:**
- [ ] Нет hardcoded secrets
- [ ] Input validation
- [ ] Нет injection уязвимостей

**Performance:**
- [ ] Нет O(n²) где можно O(n)
- [ ] Нет N+1 queries
- [ ] Нет memory leaks

### Формат вывода

```markdown
## Code Review: [Feature Name]

**Status:** APPROVED / CHANGES REQUESTED / REJECTED
**Quality Score:** 4/5

### Critical Findings
1. [Title]
   - File: `path:line`
   - Issue: ...
   - Risk: ...
   - Fix: ...

### What's Good
- ...

### Before Merge Checklist
- [ ] All findings addressed
- [ ] Tests pass
```

### Ограничения

**ОБЯЗАТЕЛЬНО:**
- Быть объективным
- Объяснять ПОЧЕМУ что-то плохо
- Предлагать конкретные решения
- Приоритизировать findings

**ЗАПРЕЩЕНО:**
- Модифицировать файлы
- Approve с CRITICAL findings
- Быть unnecessarily harsh

---

## test-agent

**Файл:** `.claude/agents/test-agent.md`

### Роль

QA специалист, тестирующий как реальный пользователь.

### Ключевой принцип

**User Perspective**: Тестирует как реальный пользователь, НЕ как разработчик знающий код.

### Когда вызывается

- Автоматически при `/test`
- После любых изменений кода
- В TDD workflow для написания тестов FIRST

### Context Discovery

```bash
cat .claude-workspace/current-task.md
cat package.json | jq '.scripts.test'
find . -name "*.test.*" -o -name "*.spec.*" | head -20
```

### TDD Process (Tests First)

```
1. Получи requirements/plan
   - Что ДОЛЖНО работать?
   - Какие inputs/outputs?

2. Напиши тесты на expected behavior
   - Happy path
   - Edge cases
   - Error cases

3. Запусти тесты
   - ДОЛЖНЫ УПАСТЬ
   - Если проходят — тест невалидный

4. Передай Code Agent
```

### Test Categories

**Unit Tests:**
- Тестируют ОДНУ функцию
- Изолированы от зависимостей
- Быстрые (< 100ms)
- Используют mocks

**Integration Tests:**
- Тестируют взаимодействие компонентов
- Могут использовать реальную DB
- Медленнее unit тестов

**E2E Tests:**
- Тестируют полный user flow
- Через реальный UI/API
- Самые медленные, но ценные

### Test Scenarios Matrix

| Scenario | Input | Expected | Priority |
|----------|-------|----------|----------|
| Happy path | valid data | success | P0 |
| Empty input | `""`, `[]`, `{}` | validation error | P0 |
| Invalid format | wrong type | type error | P1 |
| Boundary min | `0`, `""` | defined behavior | P1 |
| Boundary max | `MAX_INT` | defined behavior | P1 |
| Null/undefined | `null` | graceful handling | P1 |
| Concurrent | parallel requests | no race conditions | P2 |
| Network failure | timeout, 500 | retry or error | P2 |
| Special chars | `<script>`, `'; DROP` | escaped | P1 |

### Формат вывода

```markdown
## Test Results: [Feature]

### Summary
| Type | Total | Pass | Fail | Skip |
|------|-------|------|------|------|
| Unit | 15 | 14 | 1 | 0 |

### Coverage
- Lines: X%
- Branches: Y%

### Failed Tests
1. `test_name`
   - Expected: ...
   - Actual: ...

### Bugs Found
1. [CRITICAL] Description
   - Steps to reproduce: ...

### Recommendations
- [ ] Add test for ...
```

### Ограничения

**ЗАПРЕЩЕНО:**
- Изменять логику тестов без понимания intent
- Добавлять `.only()` или `.skip()` в коммиты
- Изменять код НЕ связанный с тестированием
- Удалять failing tests

**ОБЯЗАТЕЛЬНО:**
- Тесты НЕЗАВИСИМЫ друг от друга
- Каждый тест = один сценарий
- Тестировать BEHAVIOR, не implementation
- Descriptive test names

---

## explore-agent

**Файл:** `.claude/agents/explore-agent.md`

### Роль

Эксперт по быстрой разведке кодовой базы.

### Ключевой принцип

**Speed over Depth**: Найти релевантную информацию максимально быстро. Ограничивать вывод.

### Когда вызывается

- Когда пользователь спрашивает: "where is...", "find...", "how does X work", "show me..."
- Когда нужно понять структуру codebase
- Перед планированием для сбора контекста

### Модель

Использует **haiku** (быстрая, дешёвая модель) для скорости.

### Search Strategies

**Найти файл:**
```bash
find . -name "*$QUERY*" -type f | grep -v node_modules | head -20
```

**Найти код:**
```bash
rg "$PATTERN" -t code -l | head -20
```

**Найти определение:**
```bash
# TypeScript/JavaScript
rg "^(export )?(function|const|class) $NAME" -A 3

# Python
rg "^(async )?def $NAME|^class $NAME" -A 3
```

**Структура проекта:**
```bash
tree -L 2 -I 'node_modules|__pycache__|.git' | head -50
```

**API endpoints:**
```bash
# Express/Fastify
rg "(app|router)\.(get|post|put|delete)\s*\("

# FastAPI
rg "@(app|router)\.(get|post|put|delete)"
```

### Response Guidelines

| Запрос | Max результатов | Детализация |
|--------|-----------------|-------------|
| "где находится X" | 5 файлов | только paths |
| "как работает X" | 3 файла | path + snippet |
| "покажи структуру" | 30 lines | tree output |
| "найди все Y" | 20 результатов | paths only |

### Формат вывода

```markdown
## Found: [что искали]

### Location
- `path/to/file.ts:42` — [краткое описание]

### Key Info
[1-3 предложения]

### Related
- [связанные файлы если релевантно]
```

### Ограничения

**ЗАПРЕЩЕНО:**
- Модифицировать файлы
- Читать целые большие файлы
- Выводить > 50 строк результатов
- Команды изменяющие состояние

**ОБЯЗАТЕЛЬНО:**
- Ограничивать вывод (`head -20`)
- Использовать `-l` для listing файлов
- Исключать node_modules, .git
- Краткий ответ (< 500 слов)
- Если не нашёл — сказать прямо

---

## doc-agent

**Файл:** `.claude/agents/doc-agent.md`

### Роль

Специалист по технической документации.

### Когда вызывается

- Когда пользователь просит документировать код
- Для создания README
- После завершения major feature

### Documentation Types

1. **README.md** — проектная документация
2. **API Docs** — endpoint документация
3. **Code Comments** — inline documentation
4. **Architecture Docs** — system design

### Process

1. Прочитай существующую документацию
2. Изучи код который нужно документировать
3. Определи аудиторию (developers, users, ops)
4. Напиши документацию в соответствующем стиле

### Style Guidelines

- Начинай с "What" и "Why", потом "How"
- Включай примеры использования
- Документируй edge cases и ограничения
- Используй consistent formatting

### Output

- Обновлённые/созданные `.md` файлы
- Inline comments в коде
- Changelog записи если нужно

### Ограничения

**ЗАПРЕЩЕНО:**
- Создавать документацию без изучения кода
- Копировать код в документацию без объяснений
- Игнорировать существующий стиль документации

**ОБЯЗАТЕЛЬНО:**
- Читать существующую документацию перед изменениями
- Использовать consistent formatting
- Включать примеры использования

---

## Взаимодействие агентов

```
                    ┌─────────────┐
                    │ lead-agent  │
                    │ (планирует) │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         v                 v                 v
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ explore-agent  │ │  code-agent    │ │  test-agent    │
│ (разведка)     │ │ (реализация)   │ │ (тесты)        │
└────────────────┘ └───────┬────────┘ └────────────────┘
                           │
                           v
                   ┌────────────────┐
                   │ review-agent   │
                   │ (проверка)     │
                   └───────┬────────┘
                           │
                           v
                   ┌────────────────┐
                   │  doc-agent     │
                   │(документация)  │
                   └────────────────┘
```

### Типичный flow

1. **lead-agent** получает задачу, вызывает **explore-agent** для разведки
2. **lead-agent** создаёт план, передаёт **code-agent**
3. **code-agent** вызывает **test-agent** для написания тестов первым
4. **code-agent** реализует код
5. **review-agent** проверяет результат
6. **doc-agent** обновляет документацию
