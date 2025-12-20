# Сценарии взаимодействия

Визуальные Mermaid-диаграммы workflow системы Claude Code Kit.

---

## 1. Архитектура системы

```mermaid
flowchart TB
    subgraph User["👤 Пользователь"]
        CMD["/plan-task, /implement, /review-task, /done"]
        CHAT["Свободный чат"]
    end

    subgraph Orchestrator["🎯 Claude Code"]
        ROUTER{Роутер}
        HOOKS["Hooks"]
    end

    subgraph Agents["🤖 Агенты"]
        DEV["dev-agent<br/>sonnet"]
        REVIEW["review-agent<br/>sonnet"]
        EXPLORE["explore-agent<br/>haiku"]
        DOC["doc-agent<br/>sonnet"]
    end

    subgraph State["📁 State"]
        JSON["state.json"]
        ARCHIVE["archive/"]
    end

    subgraph Tools["🔧 Инструменты"]
        READ["Read/Grep/Glob"]
        EDIT["Edit/Write"]
        BASH["Bash"]
        GIT["Git"]
    end

    CMD --> ROUTER
    CHAT --> ROUTER

    ROUTER -->|/implement| DEV
    ROUTER -->|/review-task| REVIEW
    ROUTER -->|"где? как?"| EXPLORE
    ROUTER -->|документация| DOC

    DEV --> JSON
    DEV --> EDIT
    DEV --> GIT
    REVIEW --> READ
    REVIEW --> GIT
    EXPLORE --> READ
    DOC --> EDIT

    EDIT --> HOOKS
    HOOKS -->|format| EDIT
```

---

## 2. Полный цикл фичи

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant C as 🎯 Claude Code
    participant D as 💻 dev-agent
    participant R as 👀 review-agent
    participant G as 📂 Git

    Note over U,G: Фаза 1: Планирование
    U->>C: /plan-task добавить авторизацию
    C->>C: Анализ codebase
    C->>C: Создание плана в state.json
    C-->>U: 📋 План готов. Approve?
    U->>C: Да, выполняй

    Note over U,G: Фаза 2: Реализация
    U->>C: /implement
    C->>C: status → "in_progress"
    C->>D: Делегировать реализацию

    loop TDD для каждого шага
        D->>D: Write test (RED)
        D->>D: Run test → FAIL ❌
        D->>D: Implement (GREEN)
        D->>D: Run test → PASS ✅
        D->>D: Refactor
        D->>G: git commit
        D->>D: Update state.json
    end

    D-->>C: Реализация завершена
    C->>C: status → "review"
    C-->>U: ✅ Код готов

    Note over U,G: Фаза 3: Code Review
    U->>C: /review-task
    C->>R: Делегировать review
    R->>R: Auto-checks (lint, tests)
    R->>R: Security scan
    R->>R: Code quality review
    R-->>C: Вердикт

    alt APPROVED
        C-->>U: ✅ APPROVED
        U->>C: /done
        C->>C: Архивация в archive/
        C->>C: currentTask → null
        C-->>U: 🎉 Задача завершена
    else CHANGES_REQUESTED
        C-->>U: ⚠️ Требуются изменения
        U->>C: /implement (исправления)
    end
```

---

## 3. TDD цикл dev-agent

```mermaid
flowchart TD
    START([📋 Получить шаг из state.json]) --> READ[Прочитать контекст]

    READ --> RED[🔴 RED: Написать тест]
    RED --> RUN_FAIL[Запустить тест]
    RUN_FAIL --> FAIL{Тест упал?}

    FAIL -->|Нет| FIX_TEST[Исправить тест]
    FIX_TEST --> RUN_FAIL

    FAIL -->|Да| GREEN[🟢 GREEN: Написать код]
    GREEN --> RUN_PASS[Запустить тест]
    RUN_PASS --> PASS{Тест прошёл?}

    PASS -->|Нет| FIX_CODE[Исправить код]
    FIX_CODE --> RUN_PASS

    PASS -->|Да| REFACTOR[🔵 REFACTOR]
    REFACTOR --> LINT[Lint + Type check]
    LINT --> COMMIT[Git commit]
    COMMIT --> UPDATE[Обновить state.json<br/>step.completed = true]

    UPDATE --> NEXT{Есть ещё шаги?}
    NEXT -->|Да| START
    NEXT -->|Нет| DONE([✅ Реализация завершена])

    style RED fill:#ffcdd2
    style GREEN fill:#c8e6c9
    style REFACTOR fill:#bbdefb
    style DONE fill:#c8e6c9
```

---

## 4. Quick Fix сценарий

```mermaid
flowchart TD
    START([🔧 /plan-task --quick]) --> ASSESS{Изменения<br/>< 20 LOC?}

    ASSESS -->|Нет| FULL[/plan-task без --quick]
    FULL --> FULL_FLOW([Полный цикл])

    ASSESS -->|Да| FIND[Найти проблемный код]
    FIND --> TEST[Написать тест]
    TEST --> FIX[Минимальное исправление]
    FIX --> VERIFY{Тесты OK?}

    VERIFY -->|Нет| FIX
    VERIFY -->|Да| COMMIT["git commit -m 'fix: ...'"]
    COMMIT --> DONE([✅ Исправлено])

    style START fill:#e3f2fd
    style DONE fill:#c8e6c9
```

---

## 5. GitHub Issue сценарий

```mermaid
flowchart TD
    START([📝 /plan-task --issue 123]) --> FETCH[gh issue view 123]

    FETCH --> VALID{Issue<br/>существует?}
    VALID -->|Нет| ERROR([❌ Issue not found])

    VALID -->|Да| ANALYZE[Анализ проблемы]
    ANALYZE --> SIZE{Размер<br/>фикса?}

    SIZE -->|< 20 LOC| QUICK[Quick Fix режим]
    SIZE -->|> 20 LOC| PLAN[Создать полный план]

    QUICK --> BRANCH[git checkout -b fix/issue-123]
    PLAN --> BRANCH

    BRANCH --> IMPLEMENT[/implement]
    IMPLEMENT --> TEST[Тесты проходят?]

    TEST -->|Нет| FIX[Исправить]
    FIX --> TEST

    TEST -->|Да| PUSH[git push]
    PUSH --> PR[gh pr create<br/>Fixes #123]
    PR --> DONE([✅ PR создан])

    style START fill:#fff3e0
    style DONE fill:#c8e6c9
    style ERROR fill:#ffcdd2
```

---

## 6. Code Review процесс

```mermaid
flowchart TD
    START([👀 /review-task]) --> SCOPE{Аргумент?}

    SCOPE -->|N или пусто| COMMITS[Последние N коммитов]
    SCOPE -->|staged| STAGED[Staged changes]
    SCOPE -->|branch| BRANCH[Вся ветка vs main]

    COMMITS --> AUTO
    STAGED --> AUTO
    BRANCH --> AUTO

    subgraph AUTO["Автоматические проверки"]
        TESTS[npm test]
        LINT[npm run lint]
        TYPES[Type check]
        SECRETS[Secrets detection]
    end

    AUTO --> AUTO_RESULT{Проверки<br/>прошли?}

    AUTO_RESULT -->|Нет| REJECT([❌ REJECTED<br/>Автоматические проверки упали])

    AUTO_RESULT -->|Да| MANUAL[Ручной review]

    subgraph MANUAL_CHECKS["Проверка кода"]
        CORRECT[Корректность логики]
        QUALITY[Качество кода]
        TESTING[Покрытие тестами]
        SECURITY[Безопасность]
        PERF[Производительность]
    end

    MANUAL --> MANUAL_CHECKS
    MANUAL_CHECKS --> VERDICT{Вердикт}

    VERDICT -->|Critical issues| REJECTED([❌ REJECTED])
    VERDICT -->|Minor issues| CHANGES([⚠️ CHANGES_REQUESTED])
    VERDICT -->|All good| APPROVED([✅ APPROVED])

    style APPROVED fill:#c8e6c9
    style CHANGES fill:#fff3e0
    style REJECTED fill:#ffcdd2
    style REJECT fill:#ffcdd2
```

---

## 7. Жизненный цикл задачи

```mermaid
stateDiagram-v2
    [*] --> planned: /plan-task

    planned --> in_progress: /implement
    planned --> planned: Уточнение плана

    in_progress --> in_progress: TDD итерации
    in_progress --> review: Код готов

    review --> in_progress: CHANGES_REQUESTED
    review --> done: APPROVED + /done

    done --> [*]: Архивировано

    note right of planned
        state.json создан
        Ожидает одобрения
    end note

    note right of in_progress
        dev-agent работает
        RED → GREEN → REFACTOR
    end note

    note right of review
        review-agent проверяет
        Auto-checks + Manual review
    end note

    note right of done
        Архив в archive/
        currentTask = null
    end note
```

---

## 8. Выбор команды

```mermaid
flowchart TD
    START([🤔 Что делать?]) --> TYPE{Тип задачи?}

    TYPE -->|Новая фича| SIZE{Размер?}
    SIZE -->|> 50 LOC| PLAN[/plan-task feature]
    SIZE -->|< 50 LOC| PLAN_QUICK[/plan-task feature]

    TYPE -->|Баг| BUG_SIZE{Размер фикса?}
    BUG_SIZE -->|< 20 LOC| QUICK[/plan-task --quick]
    BUG_SIZE -->|> 20 LOC| PLAN

    TYPE -->|GitHub Issue| ISSUE[/plan-task --issue N]

    TYPE -->|Проверка кода| REVIEW[/review-task]

    TYPE -->|Исследование| EXPLORE[Задать вопрос<br/>→ explore-agent]

    TYPE -->|Документация| DOC[Запросить<br/>→ doc-agent]

    PLAN --> IMPLEMENT[/implement]
    PLAN_QUICK --> IMPLEMENT
    ISSUE --> IMPLEMENT
    QUICK --> IMPLEMENT

    IMPLEMENT --> REVIEW
    REVIEW --> VERDICT{Вердикт?}

    VERDICT -->|APPROVED| DONE[/done]
    VERDICT -->|CHANGES| IMPLEMENT

    DONE --> END([✅ Готово])

    style START fill:#e1f5fe
    style END fill:#c8e6c9
```

---

## 9. Взаимодействие агентов

```mermaid
flowchart TB
    subgraph Input["👤 Вход"]
        CMD[Команда или запрос]
    end

    subgraph Router["🎯 Claude Code"]
        DETECT{Определить<br/>тип}
    end

    subgraph Agents["🤖 Агенты"]
        DEV[💻 dev-agent<br/>TDD реализация]
        REVIEW[👀 review-agent<br/>Код-ревью]
        EXPLORE[🔍 explore-agent<br/>Разведка]
        DOC[📝 doc-agent<br/>Документация]
    end

    CMD --> DETECT

    DETECT -->|/implement| DEV
    DETECT -->|/review-task| REVIEW
    DETECT -->|"где? найди? как?"| EXPLORE
    DETECT -->|"документация"| DOC

    EXPLORE -.->|контекст| DEV
    DEV -.->|код готов| REVIEW

    style DEV fill:#e8f5e9
    style REVIEW fill:#fce4ec
    style EXPLORE fill:#f3e5f5
    style DOC fill:#e3f2fd
```

---

## Легенда

| Символ | Значение |
|--------|----------|
| `[...]` | Процесс/Действие |
| `{...}` | Решение/Условие |
| `([...])` | Начало/Конец |
| `-->` | Переход |
| `-.->` | Делегирование |
| 🔴 | RED (failing test) |
| 🟢 | GREEN (passing test) |
| 🔵 | REFACTOR |
| ✅ | Success / APPROVED |
| ❌ | Failure / REJECTED |
| ⚠️ | CHANGES_REQUESTED |

---

## Рендеринг диаграмм

Mermaid диаграммы можно просматривать в:
- GitHub/GitLab README
- VS Code (расширение Mermaid)
- [mermaid.live](https://mermaid.live)
- Obsidian, Notion
