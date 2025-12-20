# План рефакторинга Claude-Code-Kit v2.0 (исправленный)

> Основан на анализе best practices Anthropic, 20+ community репозиториев и официальной документации
> 
> **Исправлено**: Названия агентов `xxx-agent`, оригинальные названия команд, description на русском

---

## Текущая структура проекта (сохраняем)

### Агенты (паттерн `xxx-agent`)
- `lead-agent.md` — Архитектор и планировщик
- `code-agent.md` — Разработчик (TDD)
- `review-agent.md` — Код-ревьюер
- `test-agent.md` — QA специалист
- `explore-agent.md` — Исследователь кодовой базы
- `doc-agent.md` — Документатор

### Команды (оригинальные названия)
- `init-project.md` — Инициализация проекта
- `plan.md` — Планирование фичи
- `implement.md` — Реализация по плану
- `review.md` — Код-ревью
- `test.md` — Тестирование
- `quick-fix.md` — Быстрые исправления
- `project-status.md` — Статус проекта (НЕ status!)
- `fix-issue.md` — Исправление GitHub issues

---

## Резюме изменений

| Аспект | Было | Станет |
|--------|------|--------|
| Агенты | 6 (без tool scoping) | 8 (с tool scoping + model hints) |
| Skills | 0 | 6 (progressive disclosure) |
| Quality Gates | 0 | 3 (между фазами) |
| Hooks | Частично | PreToolUse + PostToolUse |
| CLAUDE.md | ~100+ строк | <60 строк + ссылки |
| Tracking | features.json | iterations/ + handoffs/ |

---

## Фаза 1: Добавление Skills (2-3 часа)

### 1.1 Структура Skills

```
.claude/
└── skills/
    ├── tdd-workflow/
    │   ├── SKILL.md
    │   ├── red-green-refactor.md
    │   └── examples.md
    ├── code-review/
    │   ├── SKILL.md
    │   ├── security-checks.md
    │   └── auto-reject-rules.md
    ├── git-workflow/
    │   ├── SKILL.md
    │   ├── atomic-commits.md
    │   └── branch-strategy.md
    ├── context-discovery/
    │   ├── SKILL.md
    │   └── patterns.md
    ├── session-management/
    │   ├── SKILL.md
    │   └── handoff-template.md
    └── python-patterns/
        ├── SKILL.md
        ├── async-patterns.md
        └── testing-patterns.md
```

### 1.2 Skill: tdd-workflow/SKILL.md

```markdown
---
name: tdd-workflow
description: "TDD workflow для разработки. Использовать ПРОАКТИВНО при реализации фич, написании кода, или когда пользователь упоминает 'TDD', 'тесты первыми', 'red-green-refactor'."
---

# TDD Workflow

## Краткий справочник

### Цикл Red-Green-Refactor

1. **RED**: Напиши тест → `pytest tests/test_X.py -v` → ДОЛЖЕН УПАСТЬ
2. **GREEN**: Напиши минимум кода → тест ДОЛЖЕН ПРОЙТИ
3. **REFACTOR**: Улучши код → тесты ВСЁ ЕЩЁ проходят
4. **COMMIT**: `git add . && git commit -m "type(scope): description"`

## Критические правила

- **НИКОГДА** не пиши код без падающего теста
- **НИКОГДА** не модифицируй тесты чтобы они прошли
- **ОДИН** тест = **ОДИН** сценарий
- Тест описывает **ПОВЕДЕНИЕ**, не реализацию

## Детали

Для детального процесса: [red-green-refactor.md](red-green-refactor.md)
Для примеров тестов: [examples.md](examples.md)
```

### 1.3 Skill: code-review/SKILL.md

```markdown
---
name: code-review
description: "Чеклисты код-ревью и сканирование безопасности. Использовать при ревью кода, проверке PR, или после завершения реализации."
allowed-tools: Read, Grep, Glob
---

# Code Review Skill

## Автоматические проверки

```bash
# Тесты
pytest tests/ -v 2>&1 | tail -20

# Линтинг
ruff check . 2>&1 | head -20

# Security сканирование
rg -i "(api.?key|password|secret|token)\s*=" --type py | head -5
rg "(execute|query).*\$|f\".*{.*}.*\"" --type py | head -5
```

## Auto-REJECT критерии

| Находка | Действие |
|---------|----------|
| Hardcoded секреты | ❌ REJECT |
| SQL/Command injection | ❌ REJECT |
| Нет тестов для нового кода | ⚠️ REQUEST CHANGES |
| print() в production | ⚠️ REQUEST CHANGES |

## Детальные чеклисты

Для security checks: [security-checks.md](security-checks.md)
Для полных правил: [auto-reject-rules.md](auto-reject-rules.md)
```

### 1.4 Skill: session-management/SKILL.md

```markdown
---
name: session-management
description: "Управление состоянием сессии и передача контекста между сессиями. Использовать в начале/конце сессии, или когда пользователь говорит 'продолжи', 'возобнови', 'где остановились'."
---

# Session Management

## При старте сессии

```bash
# 1. Прочитать текущую задачу
cat .claude-workspace/current-task.md | head -30

# 2. Прочитать последний handoff
ls -t .claude-workspace/handoffs/ | head -1 | xargs -I {} cat .claude-workspace/handoffs/{}

# 3. Git статус
git status --short
git log --oneline -3
```

## При завершении сессии

Создай handoff файл в `.claude-workspace/handoffs/`:

```markdown
# Handoff: YYYY-MM-DD-HH-MM

## Выполнено
- [x] Что сделано
- [x] Какие файлы изменены

## Контекст для продолжения
- Текущий шаг: N из M
- Блокеры: ...
- Следующее действие: ...

## Артефакты
- Коммиты: [хэши]
- Тесты: passed/failed
```

## Шаблон handoff

Детальный шаблон: [handoff-template.md](handoff-template.md)
```

### 1.5 Skill: git-workflow/SKILL.md

```markdown
---
name: git-workflow
description: "Конвенции коммитов и атомарные изменения. Использовать при коммитах, работе с ветками, или когда нужен правильный формат коммита."
---

# Git Workflow

## Формат коммита

```
type(scope): краткое описание

- Детали изменения 1
- Детали изменения 2

Шаг N/M задачи
```

## Types

| Type | Описание |
|------|----------|
| `feat` | Новая функциональность |
| `fix` | Исправление бага |
| `refactor` | Рефакторинг без изменения поведения |
| `test` | Тесты |
| `docs` | Документация |
| `chore` | Прочее |

## Правила атомарных коммитов

- Один коммит = одно логическое изменение
- Код компилируется после каждого коммита
- Тесты проходят после каждого коммита
- Можно откатить без побочных эффектов

Детали: [atomic-commits.md](atomic-commits.md)
```

### 1.6 Skill: context-discovery/SKILL.md

```markdown
---
name: context-discovery
description: "Исследование кодовой базы и сбор контекста. Использовать в начале работы над задачей или при исследовании незнакомого кода."
---

# Context Discovery

## Быстрый обзор проекта

```bash
# Структура
tree -L 2 -I 'node_modules|__pycache__|.git|.venv' | head -40

# Текущее состояние
cat .claude-workspace/current-task.md 2>/dev/null | head -20
git status --short
git log --oneline -5
```

## Поиск релевантного кода

```bash
# По паттерну
rg "pattern" --type py -l

# По имени функции/класса
rg "def function_name|class ClassName" --type py

# Импорты модуля
rg "from module import|import module" --type py
```

## Паттерны исследования

Детали: [patterns.md](patterns.md)
```

### 1.7 Skill: python-patterns/SKILL.md

```markdown
---
name: python-patterns
description: "Python best practices и паттерны. Использовать при написании Python кода, рефакторинге, или оптимизации."
---

# Python Patterns

## Стиль кода

- Python 3.11+
- Type hints обязательны
- Docstrings: Google style
- Max 88 символов в строке
- Imports: stdlib → third-party → local

## Проверка качества

```bash
# Линтинг + исправление
ruff check src/ --fix

# Форматирование
ruff format src/

# Типы
mypy src/
```

## Тестирование

```bash
# Все тесты
pytest tests/ -v

# Один файл
pytest tests/test_X.py -v

# Один тест
pytest tests/test_X.py::test_name -v

# С покрытием
pytest tests/ --cov=src --cov-report=term-missing
```

Детали: [async-patterns.md](async-patterns.md), [testing-patterns.md](testing-patterns.md)
```

---

## Фаза 2: Улучшение агентов (2-3 часа)

### 2.1 Добавляемые агенты

| Агент | Назначение | Tools |
|-------|-----------|-------|
| `orchestrator-agent.md` | **НОВЫЙ**: Главный оркестратор с quality gates | Task, Read, Grep, Glob, Bash |
| `security-agent.md` | **НОВЫЙ**: Security specialist | Read, Grep, Glob, Bash(bandit,safety) |

### 2.2 Agent: orchestrator-agent.md (НОВЫЙ)

```markdown
---
name: orchestrator-agent
description: "Главный оркестратор workflow. Использовать ПРОАКТИВНО для сложных задач, многошаговых фич, или когда пользователь говорит 'сделай', 'создай фичу', 'реализуй'. Координирует других агентов через quality gates."
model: sonnet
tools: Task, Read, Grep, Glob, Bash
---

# Orchestrator Agent

Ты — главный оркестратор workflow. Координируешь работу специализированных агентов через quality gates.

## Workflow Phases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  PLANNING   │ --> │DEVELOPMENT  │ --> │ VALIDATION  │
│(lead-agent) │     │(code+test)  │     │(review)     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                  │                   │
   Quality Gate 1    Quality Gate 2     Quality Gate 3
   (План одобрен)    (Тесты проходят)   (Ревью пройдено)
```

## Quality Gates

### Gate 1: Planning Complete
- [ ] Задача декомпозирована на шаги ≤30 мин
- [ ] Каждый шаг = 1 атомарный коммит
- [ ] Риски идентифицированы
- [ ] План записан в current-task.md

### Gate 2: Development Complete
- [ ] Все тесты проходят
- [ ] Линтинг без ошибок
- [ ] Каждый шаг закоммичен

### Gate 3: Validation Complete
- [ ] Code review пройден
- [ ] Security checks пройдены
- [ ] Документация обновлена

## Делегирование

Используй Task tool для вызова агентов:

```
Task(agent="lead-agent", prompt="Исследуй и создай план для: {task}")
Task(agent="code-agent", prompt="Реализуй шаг N: {step_description}")
Task(agent="test-agent", prompt="Напиши тесты для: {feature}")
Task(agent="review-agent", prompt="Проведи ревью последних изменений")
```

## Token Budget

- Планирование: 800 токенов
- Каждый шаг разработки: 1500 токенов
- Ревью: 600 токенов

## При блокере

Если quality gate не пройден:
1. Запиши причину в handoff
2. Верни задачу на предыдущую фазу
3. Уведоми пользователя
```

### 2.3 Agent: security-agent.md (НОВЫЙ)

```markdown
---
name: security-agent
description: "Специалист по безопасности. Использовать ПРОАКТИВНО для аудитов безопасности, сканирования уязвимостей, когда пользователь упоминает 'security', 'уязвимости', 'аудит', 'безопасность'."
model: sonnet
tools: Read, Grep, Glob, Bash(git:diff,bandit:*,safety:*)
---

# Security Agent

Ты — специалист по безопасности. Фокус на обнаружении уязвимостей.

## Сканирование

### 1. Secrets Detection
```bash
rg -i "(api.?key|password|secret|token|credential)\s*=" --type py
rg "Bearer |sk-|pk_|AKIA" --type py
```

### 2. Injection Vulnerabilities
```bash
# SQL Injection
rg "execute\(.*%|execute\(.*\.format|f\".*SELECT.*{" --type py

# Command Injection
rg "subprocess\.(call|run|Popen).*shell=True" --type py
rg "os\.system\(" --type py
```

### 3. Dependency Vulnerabilities
```bash
# Python
pip-audit 2>/dev/null || pip install pip-audit && pip-audit
safety check 2>/dev/null || pip install safety && safety check
```

### 4. OWASP Top 10
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection
- [ ] A07: Auth Failures

## Формат отчёта

```markdown
## Security Audit Report

**Уровень риска:** 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW

### Находки

#### [CRITICAL] Название находки
- **Расположение:** `file:line`
- **Описание:** ...
- **Влияние:** ...
- **Исправление:** ...
- **CWE:** CWE-XXX
```
```

### 2.4 Улучшение lead-agent.md

**Добавить tool scoping и улучшить description**

```markdown
---
name: lead-agent
description: "Архитектор и планировщик задач. Использовать ПРОАКТИВНО при 'планируй', 'декомпозируй', 'как сделать', 'архитектура', или для задач требующих исследования перед реализацией."
model: sonnet
tools: Read, Grep, Glob, Bash(find,tree,cat,head,git:log,git:status)
---

# Lead Agent

... (остальное содержимое как есть, но проверить что description на русском)
```

### 2.5 Улучшение code-agent.md

**Добавить tool scoping**

```markdown
---
name: code-agent
description: "Разработчик с TDD. Использовать ПРОАКТИВНО при 'реализуй', 'напиши код', 'сделай', 'исправь', или для задач реализации."
model: sonnet
tools: Read, Write, Edit, MultiEdit, Grep, Glob, Bash(pytest:*,ruff:*,git:add,git:commit,git:status,git:diff)
---

# Code Agent

... (остальное содержимое)
```

### 2.6 Улучшение review-agent.md

**Критично: Read-only tools**

```markdown
---
name: review-agent
description: "Независимый код-ревьюер. Использовать ПРОАКТИВНО после реализации, для PR, когда пользователь говорит 'проверь', 'ревью', 'посмотри код'."
model: sonnet
tools: Read, Grep, Glob, Bash(pytest:*,ruff:*,git:diff,git:log,git:show)
---

# Review Agent

... (остальное содержимое)
```

### 2.7 Улучшение test-agent.md

```markdown
---
name: test-agent
description: "QA специалист и тестировщик. Использовать ПРОАКТИВНО при 'напиши тесты', 'протестируй', 'проверь покрытие', или для задач тестирования."
model: sonnet
tools: Read, Write, Edit, Grep, Glob, Bash(pytest:*,coverage:*)
---

# Test Agent

... (остальное содержимое)
```

### 2.8 Улучшение explore-agent.md

**Read-only tools + исправить model на inherit**

```markdown
---
name: explore-agent
description: "Исследователь кодовой базы. Использовать ПРОАКТИВНО для быстрого поиска, исследования незнакомого кода, или когда нужно найти релевантные файлы."
model: inherit
tools: Read, Grep, Glob, Bash(find,tree,cat,head,tail,wc)
---

# Explore Agent

... (остальное содержимое)
```

### 2.9 Улучшение doc-agent.md

```markdown
---
name: doc-agent
description: "Документатор. Использовать ПРОАКТИВНО при 'документируй', 'напиши README', 'обнови доки', или для задач документации."
model: sonnet
tools: Read, Write, Edit, Grep, Glob
---

# Doc Agent

... (остальное содержимое)
```

---

## Фаза 3: Settings и Hooks (1 час)

### 3.1 Создать/обновить .claude/settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$CLAUDE_FILE_PATH\"; if [[ \"$FILE\" == *.py ]] && [[ \"$FILE\" != test_* ]] && [[ \"$FILE\" != *_test.py ]] && [[ \"$FILE\" != tests/* ]]; then echo \"⚠️  TDD НАПОМИНАНИЕ: Убедись что тесты написаны ПЕРЕД реализацией\"; fi'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$CLAUDE_FILE_PATH\"; if [[ \"$FILE\" == *.py ]]; then ruff format \"$FILE\" 2>/dev/null || true; ruff check \"$FILE\" --fix 2>/dev/null || true; fi'"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Glob",
      "Grep",
      "Task",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Bash(git:*)",
      "Bash(pip:*)",
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(find:*)",
      "Bash(tree:*)",
      "Bash(ls:*)",
      "Bash(rg:*)",
      "Bash(grep:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(sudo:*)",
      "Bash(chmod 777:*)"
    ]
  }
}
```

---

## Фаза 4: Улучшение Tracking (1 час)

### 4.1 Новая структура .claude-workspace

```
.claude-workspace/
├── current-task.md              # Текущая задача (упростить)
├── progress.md                  # Лог прогресса (оставить)
├── decisions.md                 # ADR (оставить)
├── handoffs/                    # НОВОЕ: Контекст между сессиями
│   └── .gitkeep
├── iterations/                  # НОВОЕ: История итераций
│   └── .gitkeep
└── README.md                    # Описание структуры
```

### 4.2 Удалить features.json

**Причина**: Неудобный формат с ручными ID, дублирует git history. Заменяем на iterations/.

### 4.3 Формат iteration

`.claude-workspace/iterations/YYYY-MM-DD-feature-name.md`:

```markdown
# Iteration: feature-name

**Создано:** YYYY-MM-DD HH:MM
**Статус:** 🟡 IN_PROGRESS / ✅ COMPLETED / ❌ ABANDONED
**Quality Score:** 0-100

## Цель
[Одно предложение]

## Quality Gates

### Gate 1: Planning ✅
- [x] План одобрен
- Score: 95/100

### Gate 2: Development 🟡
- [ ] Тесты проходят
- [ ] Все шаги выполнены
- Score: pending

### Gate 3: Validation ⬜
- [ ] Ревью пройдено
- [ ] Security check
- Score: pending

## Progress Log

### YYYY-MM-DD HH:MM
- Выполнено: Шаг 1, Шаг 2
- Следующее: Шаг 3
- Блокеры: Нет

## Артефакты
- Коммиты: abc123, def456
- Изменённых файлов: 5
- Покрытие тестами: 85%
```

### 4.4 Формат handoff

`.claude-workspace/handoffs/YYYY-MM-DD-HH-MM.md`:

```markdown
# Session Handoff

**Сессия:** YYYY-MM-DD HH:MM - HH:MM
**Длительность:** X часов
**Задача:** [название из current-task.md]

## Выполнено в этой сессии
- [x] Шаг N: описание
- [x] Шаг M: описание

## Текущее состояние
- **Позиция:** Шаг K из L
- **Тесты:** ✅ Все проходят / ❌ X падают
- **Незакоммиченные изменения:** Да/Нет

## Контекст для следующей сессии

### Немедленное следующее действие
[Конкретное действие для продолжения]

### Открытые вопросы
- Вопрос 1?
- Вопрос 2?

### Блокеры
- Блокер 1 (если есть)

## Изменённые файлы
- `path/to/file1.py` — описание
- `path/to/file2.py` — описание

## Команды для возобновления
```bash
# Восстановить контекст
cat .claude-workspace/current-task.md
git status

# Продолжить с
pytest tests/test_X.py -v
```
```

---

## Фаза 5: Сокращение CLAUDE.md (30 мин)

### 5.1 Новый CLAUDE.md (<60 строк)

```markdown
# Claude Code Kit

Мультиагентная система для разработки с TDD workflow и quality gates.

## Критически важно

**ВСЕГДА** в начале сессии:
1. `cat .claude-workspace/current-task.md | head -20`
2. `ls -t .claude-workspace/handoffs/ | head -1 | xargs cat`
3. `git status --short`

**ВСЕГДА** перед завершением:
1. Создай handoff в `.claude-workspace/handoffs/`
2. Обнови `current-task.md` (отметь выполненные шаги)
3. Закоммить все изменения

## Команды

```bash
# Тесты
pytest tests/ -v                  # Все
pytest tests/test_X.py::test_Y -v # Один тест

# Качество
ruff check src/ --fix             # Линтинг
ruff format src/                  # Форматирование
mypy src/                         # Типы
```

## Стиль кода

- Python 3.11+, type hints обязательны
- Docstrings: Google style
- Max 88 символов в строке
- Imports: stdlib → third-party → local

## Workflow

```
/plan [task]  →  Quality Gate 1  →  /implement  →  Quality Gate 2  →  /review  →  Quality Gate 3
```

## Агенты

Автоматически делегируются по description. См. `.claude/agents/`

## Skills

Загружаются по требованию. См. `.claude/skills/`
```

---

## Фаза 6: Улучшение команд (1-2 часа)

### 6.1 Сохраняем оригинальные названия

| Файл | Изменения |
|------|-----------|
| `init-project.md` | Обновить description на русский |
| `plan.md` | Добавить quality gate 1 |
| `implement.md` | Добавить quality gate 2 |
| `review.md` | Добавить quality gate 3 |
| `project-status.md` | Обновить description на русский |
| `test.md` | Обновить description на русский |
| `quick-fix.md` | Обновить description на русский |
| `fix-issue.md` | Обновить description на русский |
| `create-handoff.md` | **НОВЫЙ**: Создание handoff |

### 6.2 Command: plan.md (улучшение)

```markdown
---
description: "Создать план реализации фичи или задачи. Аргумент — описание задачи."
allowed-tools: Read, Grep, Glob, Bash, Task
---

# /plan $ARGUMENTS

Создай план для: **$ARGUMENTS**

## Workflow

1. **Проверь текущую задачу:**
   ```bash
   cat .claude-workspace/current-task.md 2>/dev/null | head -5
   ```
   Если есть незавершённая — спроси: продолжить или заменить?

2. **Делегируй планирование:**
   ```
   Task(agent="lead-agent", prompt="Исследуй проект и создай план для: $ARGUMENTS")
   ```

3. **Quality Gate 1:**
   - [ ] План содержит ≤8 шагов
   - [ ] Каждый шаг ≤30 минут
   - [ ] Риски идентифицированы

4. **Создай iteration:**
   ```bash
   DATE=$(date '+%Y-%m-%d')
   SLUG=$(echo "$ARGUMENTS" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | head -c 30)
   touch ".claude-workspace/iterations/${DATE}-${SLUG}.md"
   ```

5. Спроси: «План готов. Начать реализацию с `/implement`?»
```

### 6.3 Command: implement.md (улучшение)

```markdown
---
description: "Реализовать текущую задачу с TDD workflow."
allowed-tools: Read, Write, Edit, MultiEdit, Bash, Grep, Glob, Task
---

# /implement

Реализуй задачу из `.claude-workspace/current-task.md` с TDD.

## Workflow

1. **Загрузи контекст:**
   ```bash
   cat .claude-workspace/current-task.md
   ```

2. **Для каждого невыполненного шага `[ ]`:**

   a. Делегируй написание теста:
   ```
   Task(agent="test-agent", prompt="Напиши падающий тест для: {step}")
   ```
   
   b. Проверь что тест падает:
   ```bash
   pytest tests/test_X.py -v  # ДОЛЖЕН УПАСТЬ
   ```
   
   c. Делегируй реализацию:
   ```
   Task(agent="code-agent", prompt="Реализуй минимум кода для прохождения теста: {step}")
   ```
   
   d. Проверь что тест проходит:
   ```bash
   pytest tests/test_X.py -v  # ДОЛЖЕН ПРОЙТИ
   ```
   
   e. Закоммить:
   ```bash
   git add .
   git commit -m "feat(scope): step description"
   ```
   
   f. Обнови current-task.md: `[ ]` → `[x]`

3. **Quality Gate 2:**
   ```bash
   pytest tests/ -v
   ruff check .
   ```
   - [ ] Все тесты проходят
   - [ ] Линтинг без ошибок

4. Предложи: «Реализация завершена. Запустить `/review`?»
```

### 6.4 Command: review.md (улучшение)

```markdown
---
description: "Провести независимое код-ревью последних изменений."
allowed-tools: Read, Grep, Glob, Bash, Task
---

# /review

Проведи независимое ревью последних изменений.

## Scope

- По умолчанию: последние 3 коммита
- `/review 5` — последние 5 коммитов
- `/review staged` — только staged изменения

## Workflow

1. **Делегируй ревью:**
   ```
   Task(agent="review-agent", prompt="Проведи ревью последних изменений")
   ```

2. **Делегируй security check:**
   ```
   Task(agent="security-agent", prompt="Проверь безопасность последних изменений")
   ```

3. **Quality Gate 3:**
   - [ ] Code review: APPROVED
   - [ ] Security check: PASSED
   - [ ] Критических находок нет

4. При APPROVED — предложи очистить current-task.md и обновить iteration
```

### 6.5 Command: create-handoff.md (НОВЫЙ)

```markdown
---
description: "Создать handoff для передачи контекста следующей сессии."
allowed-tools: Read, Write, Bash
---

# /create-handoff

Создай handoff для передачи контекста следующей сессии.

## Workflow

1. **Собери информацию:**
   ```bash
   cat .claude-workspace/current-task.md | head -30
   git status --short
   git log --oneline -5
   pytest tests/ -v 2>&1 | tail -10
   ```

2. **Создай handoff файл:**
   ```bash
   TIMESTAMP=$(date '+%Y-%m-%d-%H-%M')
   ```
   
   Создай файл `.claude-workspace/handoffs/${TIMESTAMP}.md` с шаблоном из skill session-management.

3. **Финальные действия:**
   ```bash
   git add .claude-workspace/handoffs/
   git commit -m "chore: добавить session handoff"
   ```

4. Покажи summary и попрощайся.
```

### 6.6 Обновить description в остальных командах

**init-project.md:**
```markdown
---
description: "Инициализировать проект для Claude Code Kit."
...
```

**project-status.md:**
```markdown
---
description: "Показать текущий статус проекта и задачи."
...
```

**test.md:**
```markdown
---
description: "Запустить тесты для указанной фичи или всего проекта."
...
```

**quick-fix.md:**
```markdown
---
description: "Быстро исправить баг без полного TDD цикла."
...
```

**fix-issue.md:**
```markdown
---
description: "Исправить GitHub issue по номеру."
...
```

---

## Фаза 7: Документация (30 мин)

### 7.1 Обновить docs/

- `docs/WORKFLOW.md` — добавить quality gates
- `docs/AGENTS.md` — обновить с tool scoping
- `docs/COMMANDS.md` — обновить descriptions
- `docs/SKILLS.md` — **НОВЫЙ**: документация по skills

---

## Итоговая структура

```
Claude-Code-Kit/
├── CLAUDE.md                          # <60 строк
├── .claude/
│   ├── settings.json                  # Hooks + permissions
│   ├── agents/                        # 8 агентов
│   │   ├── orchestrator-agent.md      # НОВЫЙ
│   │   ├── lead-agent.md              # УЛУЧШЕН
│   │   ├── code-agent.md              # УЛУЧШЕН
│   │   ├── test-agent.md              # УЛУЧШЕН
│   │   ├── review-agent.md            # УЛУЧШЕН
│   │   ├── explore-agent.md           # УЛУЧШЕН
│   │   ├── doc-agent.md               # УЛУЧШЕН
│   │   └── security-agent.md          # НОВЫЙ
│   ├── commands/                      # 9 команд
│   │   ├── init-project.md            # УЛУЧШЕН
│   │   ├── plan.md                    # УЛУЧШЕН
│   │   ├── implement.md               # УЛУЧШЕН
│   │   ├── review.md                  # УЛУЧШЕН
│   │   ├── project-status.md          # УЛУЧШЕН
│   │   ├── test.md                    # УЛУЧШЕН
│   │   ├── quick-fix.md               # УЛУЧШЕН
│   │   ├── fix-issue.md               # УЛУЧШЕН
│   │   └── create-handoff.md          # НОВЫЙ
│   └── skills/                        # 6 skills (НОВОЕ)
│       ├── tdd-workflow/
│       ├── code-review/
│       ├── git-workflow/
│       ├── context-discovery/
│       ├── session-management/
│       └── python-patterns/
├── .claude-workspace/
│   ├── current-task.md
│   ├── progress.md
│   ├── decisions.md
│   ├── handoffs/                      # НОВОЕ
│   └── iterations/                    # НОВОЕ
└── docs/
    ├── README.md
    ├── WORKFLOW.md
    ├── AGENTS.md
    ├── COMMANDS.md
    └── SKILLS.md                      # НОВОЕ
```

---

## Чеклист выполнения

### Фаза 1: Skills (2-3ч)
- [ ] Создать `.claude/skills/` структуру
- [ ] tdd-workflow/SKILL.md (description на русском!)
- [ ] code-review/SKILL.md
- [ ] git-workflow/SKILL.md
- [ ] context-discovery/SKILL.md
- [ ] session-management/SKILL.md
- [ ] python-patterns/SKILL.md

### Фаза 2: Агенты (2-3ч)
- [ ] orchestrator-agent.md (НОВЫЙ, description на русском!)
- [ ] security-agent.md (НОВЫЙ, description на русском!)
- [ ] lead-agent.md (добавить tools, обновить description на русский)
- [ ] code-agent.md (добавить tools)
- [ ] test-agent.md (добавить tools)
- [ ] review-agent.md (read-only tools!)
- [ ] explore-agent.md (read-only tools, model: inherit)
- [ ] doc-agent.md (добавить tools)

### Фаза 3: Settings (1ч)
- [ ] Создать/обновить .claude/settings.json
- [ ] PreToolUse hooks для TDD (сообщения на русском!)
- [ ] PostToolUse hooks для форматирования

### Фаза 4: Tracking (1ч)
- [ ] Создать handoffs/ структуру
- [ ] Создать iterations/ структуру
- [ ] Удалить features.json

### Фаза 5: CLAUDE.md (30мин)
- [ ] Сократить до <60 строк

### Фаза 6: Команды (1-2ч)
- [ ] plan.md (добавить quality gate 1, description на русском!)
- [ ] implement.md (добавить quality gate 2, description на русском!)
- [ ] review.md (добавить quality gate 3, description на русском!)
- [ ] create-handoff.md (НОВЫЙ, description на русском!)
- [ ] Обновить description в остальных командах на русский

### Фаза 7: Документация (30мин)
- [ ] docs/SKILLS.md (НОВЫЙ)
- [ ] Обновить остальную документацию

---

## Критические исправления vs предыдущий план

| Ошибка | Исправление |
|--------|-------------|
| Агенты без `-agent` | Все агенты: `xxx-agent.md` |
| `status` вместо `project-status` | Сохраняем `project-status.md` |
| `plan` вместо `create-plan` | В текущем проекте уже `plan.md` — оставляем |
| Description на английском | ВСЕ description на русском |
| Сокращение 6→3 агентов | Расширение 6→8 агентов |

---

## Оценка времени

| Фаза | Время |
|------|-------|
| Фаза 1: Skills | 2-3 часа |
| Фаза 2: Агенты | 2-3 часа |
| Фаза 3: Settings | 1 час |
| Фаза 4: Tracking | 1 час |
| Фаза 5: CLAUDE.md | 30 мин |
| Фаза 6: Команды | 1-2 часа |
| Фаза 7: Документация | 30 мин |
| **ИТОГО** | **9-12 часов** |

---

## Источники

- [Anthropic: Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Anthropic: Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [wshobson/agents](https://github.com/wshobson/agents) — 85 агентов, 47 skills, plugin architecture
- [zhsama/claude-sub-agent](https://github.com/zhsama/claude-sub-agent) — Quality gates, spec-orchestrator
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — Tool scoping по ролям
- [peterkrueck/Claude-Code-Development-Kit](https://github.com/peterkrueck/Claude-Code-Development-Kit) — 3-tier documentation
