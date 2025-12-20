# Agents

Справочник по специализированным агентам Claude Code Kit.

## Обзор агентов

| Агент | Модель | Роль | Инструменты |
|-------|--------|------|-------------|
| `dev-agent` | sonnet | TDD разработчик | Read, Edit, Write, Grep, Glob, Bash |
| `review-agent` | sonnet | Код-ревьюер | Read, Grep, Glob, Bash(git, lint, test) |
| `explore-agent` | haiku | Разведчик кодовой базы | Read, Grep, Glob, Bash(find, tree, ls) |
| `doc-agent` | sonnet | Документатор | Read, Write, Edit, Grep, Glob, WebFetch |

---

## dev-agent

**Файл:** `.claude/agents/dev-agent.md`

### Роль

TDD разработчик, реализующий задачи из `state.json` полным циклом: тест → код → рефакторинг → коммит.

### Когда вызывается

- Автоматически при `/implement`
- После одобрения плана из `/plan-task`

### Ключевые принципы

**TDD Цикл:**
```
1. WRITE TEST (RED)    — тест описывает ожидаемое поведение, должен упасть
2. WRITE CODE (GREEN)  — минимум кода для прохождения теста
3. REFACTOR            — улучшение без изменения поведения
4. COMMIT              — атомарный коммит (один шаг = один коммит)
5. UPDATE state.json   — отметить шаг как выполненный
```

### Context Discovery

При вызове выполняет:
```bash
cat .claude-workspace/state.json | jq '.currentTask'
git status --short
git log --oneline -3
```

### Формат коммитов

```
type(scope): description

Types: feat, fix, refactor, test, docs, chore

Example:
feat(auth): add JWT token validation

- Add validate_token() function
- Add tests for valid/invalid tokens

Step 3/5 of F002
```

### Ограничения

**ЗАПРЕЩЕНО:**
- Пропускать TDD цикл
- Коммитить нерабочий код
- Модифицировать тесты чтобы они "прошли"
- Оставлять код без обновления state.json

**ОБЯЗАТЕЛЬНО:**
- Read файл ПЕРЕД Edit
- Тест сначала ПАДАЕТ, потом ПРОХОДИТ
- Атомарные коммиты (один шаг = один коммит)
- Обновлять state.json после КАЖДОГО шага

---

## review-agent

**Файл:** `.claude/agents/review-agent.md`

### Роль

Независимый код-ревьюер с "свежим взглядом". Проверяет код как внешний reviewer, не зная деталей реализации.

### Когда вызывается

- Автоматически при `/review-task`
- После завершения работы `dev-agent`
- Перед merge в main ветку

### Ключевой принцип

**Independence**: Проверяет код как ВНЕШНИЙ reviewer. Забывает детали реализации — смотрит свежим взглядом.

### Auto-REJECT критерии

| Находка | Severity | Действие |
|---------|----------|----------|
| Hardcoded secrets | CRITICAL | REJECT |
| SQL/Command injection | CRITICAL | REJECT |
| `console.log` в production | HIGH | CHANGES REQUESTED |
| Отсутствие тестов | HIGH | CHANGES REQUESTED |
| Снижение coverage | HIGH | CHANGES REQUESTED |

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

**Code Quality:**
- [ ] Читаемый код
- [ ] Понятные имена
- [ ] Нет дублирования (DRY)
- [ ] Функции < 50 строк

**Testing:**
- [ ] Тесты существуют
- [ ] Happy path покрыт
- [ ] Edge/error cases покрыты

**Security:**
- [ ] Нет hardcoded secrets
- [ ] Input validation
- [ ] Нет injection уязвимостей

### Формат вывода

```markdown
## Code Review

**Verdict:** APPROVED | CHANGES REQUESTED | REJECTED
**Quality:** 4/5

### Findings

#### Critical (must fix)
1. **[Title]** — `file:line` — [issue] — [solution]

### What's Good
- [положительные аспекты]

### Next Steps
При APPROVED: Запустите `/done` для завершения задачи.
```

### Ограничения

**ОБЯЗАТЕЛЬНО:**
- Быть объективным
- Объяснять ПОЧЕМУ что-то плохо
- Предлагать конкретные решения

**ЗАПРЕЩЕНО:**
- Модифицировать файлы
- Approve код с CRITICAL findings

---

## explore-agent

**Файл:** `.claude/agents/explore-agent.md`

### Роль

Эксперт по быстрой разведке кодовой базы. Находит нужную информацию максимально быстро.

### Когда вызывается

- Когда пользователь спрашивает: "где...", "найди...", "как работает..."
- Когда нужно понять структуру codebase
- Перед планированием для сбора контекста

### Модель

Использует **haiku** (быстрая, дешёвая модель) для скорости.

### Ключевой принцип

**Speed over Depth**: Найти релевантную информацию максимально быстро. Ограничивать вывод.

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
- Читать целые большие файлы (> 500 строк)
- Выводить > 50 строк результатов

**ОБЯЗАТЕЛЬНО:**
- Ограничивать вывод (`head -20`)
- Исключать node_modules, .git
- Краткий ответ (< 500 слов)
- Если не нашёл — сказать прямо

---

## doc-agent

**Файл:** `.claude/agents/doc-agent.md`

### Роль

Специалист по технической документации. Создаёт понятную, актуальную документацию.

### Когда вызывается

- Когда пользователь просит документировать код
- Для создания/обновления README
- После завершения major feature

### Documentation Types

1. **README.md** — проектная документация
2. **API Docs** — endpoint документация
3. **Code Comments** — inline documentation
4. **Architecture Docs** — system design
5. **CHANGELOG** — история изменений

### Process

1. **Read** — прочитай существующую документацию
2. **Analyze** — определи что нужно документировать
3. **Research** — изучи код который документируешь
4. **Write** — напиши документацию
5. **Verify** — проверь все примеры кода
6. **Update** — обнови Table of Contents и ссылки

### Style Guidelines

- Начинай с "What" и "Why", потом "How"
- Включай примеры использования
- Документируй edge cases и ограничения
- Используй consistent formatting

### Ограничения

**ЗАПРЕЩЕНО:**
- Документировать неработающий код
- Копировать docs без адаптации
- Оставлять устаревшие примеры

**ОБЯЗАТЕЛЬНО:**
- Читать существующую документацию перед изменениями
- Проверять все code snippets
- Включать примеры error handling

---

## Взаимодействие агентов

```
                    ┌─────────────────┐
                    │   /plan-task    │
                    │  (планирование) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              v              v              v
     ┌────────────────┐            ┌────────────────┐
     │ explore-agent  │            │  /implement    │
     │ (разведка)     │            │                │
     └────────────────┘            └───────┬────────┘
                                           │
                                           v
                                  ┌────────────────┐
                                  │  dev-agent     │
                                  │ (TDD цикл)     │
                                  └───────┬────────┘
                                          │
                                          v
                                  ┌────────────────┐
                                  │  /review-task  │
                                  │                │
                                  └───────┬────────┘
                                          │
                                          v
                                  ┌────────────────┐
                                  │ review-agent   │
                                  │ (проверка)     │
                                  └───────┬────────┘
                                          │
                                          v
                                  ┌────────────────┐
                                  │    /done       │
                                  └───────┬────────┘
                                          │
                                          v
                                  ┌────────────────┐
                                  │  doc-agent     │
                                  │(документация)  │
                                  └────────────────┘
```

### Типичный flow

1. **explore-agent** вызывается для разведки перед планированием
2. `/plan-task` создаёт план задачи
3. `/implement` делегирует **dev-agent** для TDD реализации
4. `/review-task` вызывает **review-agent** для проверки
5. `/done` архивирует задачу
6. **doc-agent** обновляет документацию (опционально)
