# Схемы сценариев взаимодействия

Визуальные диаграммы основных workflow при работе с системой агентов Claude Code.

---

## 1. Общая архитектура системы

```mermaid
flowchart TB
    subgraph User["👤 Пользователь"]
        CMD[Команды /*]
        CHAT[Свободный чат]
    end

    subgraph Orchestrator["🎯 Claude Code (Главный агент)"]
        ROUTER{Роутер}
        HOOKS[Hooks]
    end

    subgraph Agents["🤖 Субагенты"]
        LEAD[Lead Agent<br/>sonnet]
        CODE[Code Agent<br/>sonnet]
        TEST[Test Agent<br/>sonnet]
        REVIEW[Review Agent<br/>sonnet]
        EXPLORE[Explore Agent<br/>haiku]
    end

    subgraph Workspace["📁 Workspace"]
        PROGRESS[progress.md]
        CURRENT[current-task.md]
        FEATURES[features.json]
        DECISIONS[decisions.md]
    end

    subgraph Tools["🔧 Инструменты"]
        READ[Read/Grep/Glob]
        EDIT[Edit/Write]
        BASH[Bash]
        GIT[Git]
    end

    CMD --> ROUTER
    CHAT --> ROUTER
    
    ROUTER --> LEAD
    ROUTER --> CODE
    ROUTER --> TEST
    ROUTER --> REVIEW
    ROUTER --> EXPLORE
    
    LEAD --> PROGRESS
    LEAD --> CURRENT
    CODE --> EDIT
    CODE --> BASH
    TEST --> BASH
    REVIEW --> READ
    EXPLORE --> READ
    
    EDIT --> HOOKS
    HOOKS --> |format| EDIT
```

---

## 2. Сценарий: Новая фича (полный цикл)

### 2.1 Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant C as 🎯 Claude Code
    participant L as 🏗️ Lead Agent
    participant E as 🔍 Explore Agent
    participant CO as 💻 Code Agent
    participant T as 🧪 Test Agent
    participant R as 👀 Review Agent
    participant G as 📂 Git

    Note over U,G: Фаза 1: Инициализация (один раз)
    U->>C: /init-project
    C->>C: Создать .claude-workspace/
    C->>G: git status
    C-->>U: ✅ Workspace готов

    Note over U,G: Фаза 2: Планирование
    U->>C: /plan добавить авторизацию
    C->>L: Делегировать планирование
    L->>E: Исследовать codebase
    E->>E: Glob, Grep, Read
    E-->>L: Структура проекта, паттерны
    L->>L: "Think hard" - анализ
    L->>C: План с шагами
    C-->>U: 📋 План готов. Approve?

    Note over U,G: Фаза 3: Имплементация
    U->>C: /implement
    C->>CO: Делегировать реализацию
    
    loop Для каждого шага плана
        CO->>CO: Read current-task.md
        CO->>CO: Write test (RED)
        CO->>CO: Run test - FAIL ❌
        CO->>CO: Implement (GREEN)
        CO->>CO: Run test - PASS ✅
        CO->>G: git commit
        CO->>CO: Update progress.md
    end
    
    CO-->>C: Реализация завершена
    C-->>U: ✅ Код готов

    Note over U,G: Фаза 4: Тестирование
    U->>C: /test авторизация
    C->>T: Делегировать тестирование
    T->>T: Unit tests
    T->>T: Integration tests
    T->>T: E2E tests
    T->>T: Coverage check
    T-->>C: Отчёт о тестировании
    C-->>U: 📊 Тесты: 95% pass, 87% coverage

    Note over U,G: Фаза 5: Code Review
    U->>C: /review
    C->>R: Делегировать review
    R->>R: git diff analysis
    R->>R: Security scan
    R->>R: Code quality check
    R-->>C: Review findings
    C-->>U: 👀 Review: APPROVED ✅

    Note over U,G: Фаза 6: Завершение
    U->>C: Merge и deploy
    C->>G: git merge
    C-->>U: 🎉 Фича готова!
```

### 2.2 Flowchart (процесс принятия решений)

```mermaid
flowchart TD
    START([🚀 Новая фича]) --> INIT{Workspace<br/>инициализирован?}
    
    INIT -->|Нет| INIT_CMD[/init-project]
    INIT_CMD --> PLAN
    INIT -->|Да| PLAN
    
    PLAN[/plan feature/] --> THINK[Lead Agent:<br/>Think Hard]
    THINK --> EXPLORE[Explore Agent:<br/>Исследование codebase]
    EXPLORE --> CREATE_PLAN[Создать план<br/>в current-task.md]
    CREATE_PLAN --> APPROVE{User:<br/>Approve план?}
    
    APPROVE -->|Нет| REVISE[Уточнить требования]
    REVISE --> THINK
    
    APPROVE -->|Да| IMPLEMENT[/implement/]
    
    IMPLEMENT --> STEP_LOOP{Есть ещё<br/>шаги?}
    
    STEP_LOOP -->|Да| TDD_RED[🔴 Write failing test]
    TDD_RED --> TDD_GREEN[🟢 Implement to pass]
    TDD_GREEN --> TDD_REFACTOR[🔵 Refactor if needed]
    TDD_REFACTOR --> COMMIT[Git commit]
    COMMIT --> UPDATE_PROGRESS[Update progress.md]
    UPDATE_PROGRESS --> STEP_LOOP
    
    STEP_LOOP -->|Нет| TEST[/test feature/]
    
    TEST --> TEST_RESULT{Тесты<br/>проходят?}
    
    TEST_RESULT -->|Нет| FIX_BUGS[Исправить баги]
    FIX_BUGS --> TEST
    
    TEST_RESULT -->|Да| REVIEW[/review/]
    
    REVIEW --> REVIEW_RESULT{Review<br/>пройден?}
    
    REVIEW_RESULT -->|Changes Requested| FIX_ISSUES[Исправить замечания]
    FIX_ISSUES --> REVIEW
    
    REVIEW_RESULT -->|Approved| MERGE[Git merge]
    MERGE --> DONE([✅ Фича готова])
    
    style START fill:#e1f5fe
    style DONE fill:#c8e6c9
    style TDD_RED fill:#ffcdd2
    style TDD_GREEN fill:#c8e6c9
    style TDD_REFACTOR fill:#bbdefb
```

---

## 3. Сценарий: Исправление GitHub Issue

### 3.1 Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant C as 🎯 Claude Code
    participant GH as 🐙 GitHub API
    participant CO as 💻 Code Agent
    participant G as 📂 Git

    U->>C: /fix-issue 123
    
    C->>GH: gh issue view 123
    GH-->>C: Issue details
    
    C->>C: Анализ проблемы
    C->>C: Grep: поиск в codebase
    
    C->>C: "Think hard": root cause
    
    C->>G: git checkout -b fix/issue-123
    
    C->>CO: Делегировать fix
    
    CO->>CO: Write test (reproduce bug)
    CO->>CO: Run test - FAIL ❌
    CO->>CO: Fix the bug
    CO->>CO: Run test - PASS ✅
    CO->>CO: Run all tests ✅
    
    CO->>G: git commit -m "fix: ..."
    CO->>G: git push origin fix/issue-123
    
    CO->>GH: gh pr create
    GH-->>CO: PR #456 created
    
    CO-->>C: Fix complete
    C-->>U: ✅ PR #456 создан<br/>Fixes #123
```

### 3.2 Flowchart

```mermaid
flowchart TD
    START([📝 GitHub Issue #N]) --> VALIDATE{Issue #<br/>валиден?}
    
    VALIDATE -->|Нет| ERROR[❌ Issue not found]
    ERROR --> END_FAIL([Конец])
    
    VALIDATE -->|Да| FETCH[Получить детали issue]
    FETCH --> ANALYZE[Анализ проблемы]
    
    ANALYZE --> REPRODUCE{Можно<br/>воспроизвести?}
    
    REPRODUCE -->|Нет| ASK_DETAILS[Запросить больше деталей]
    ASK_DETAILS --> END_WAIT([Ждём ответа])
    
    REPRODUCE -->|Да| BRANCH[Создать ветку<br/>fix/issue-N]
    
    BRANCH --> WRITE_TEST[Написать тест<br/>воспроизводящий баг]
    WRITE_TEST --> RUN_TEST_FAIL[Запустить тест<br/>❌ FAIL]
    
    RUN_TEST_FAIL --> COMPLEXITY{Fix сложный<br/>> 20 LOC?}
    
    COMPLEXITY -->|Да| ESCALATE[/plan fix/]
    ESCALATE --> END_PLAN([Создать план])
    
    COMPLEXITY -->|Нет| FIX[Исправить код]
    FIX --> RUN_TEST_PASS{Тест<br/>проходит?}
    
    RUN_TEST_PASS -->|Нет| FIX
    RUN_TEST_PASS -->|Да| RUN_ALL{Все тесты<br/>проходят?}
    
    RUN_ALL -->|Нет| FIX_REGRESSION[Исправить регрессию]
    FIX_REGRESSION --> RUN_ALL
    
    RUN_ALL -->|Да| COMMIT[Git commit]
    COMMIT --> PUSH[Git push]
    PUSH --> PR[Создать PR]
    PR --> DONE([✅ PR создан])
    
    style START fill:#fff3e0
    style DONE fill:#c8e6c9
    style ERROR fill:#ffcdd2
    style RUN_TEST_FAIL fill:#ffcdd2
```

---

## 4. Сценарий: Quick Fix (быстрое исправление)

```mermaid
flowchart TD
    START([🔧 Quick Fix]) --> ASSESS{Изменения<br/>< 20 LOC?}
    
    ASSESS -->|Нет| ESCALATE[/plan/]
    ESCALATE --> END_PLAN([Полный цикл])
    
    ASSESS -->|Да| TYPE{Тип<br/>изменения?}
    
    TYPE -->|Новая фича| ESCALATE
    TYPE -->|Рефакторинг| ESCALATE
    TYPE -->|Баг| FIND[Найти проблемный код]
    
    FIND --> READ[Прочитать контекст]
    READ --> TEST_FIRST[Написать тест]
    TEST_FIRST --> FIX[Минимальное исправление]
    FIX --> VERIFY{Тесты OK?}
    
    VERIFY -->|Нет| FIX
    VERIFY -->|Да| COMMIT[git commit -m 'fix: ...']
    COMMIT --> DONE([✅ Исправлено])
    
    style START fill:#e3f2fd
    style DONE fill:#c8e6c9
    style ESCALATE fill:#fff3e0
```

---

## 5. Сценарий: Проверка статуса

```mermaid
flowchart LR
    START([/project-status/]) --> MODE{Аргументы?}
    
    MODE -->|compact| COMPACT[Краткий отчёт]
    MODE -->|default| FULL[Полный отчёт]
    
    subgraph COMPACT_REPORT[Краткий отчёт]
        C1[Current task]
        C2[Git status]
        C3[Test status]
    end
    
    subgraph FULL_REPORT[Полный отчёт]
        F1[Current task]
        F2[Recent activity]
        F3[Features overview]
        F4[Git status]
        F5[Test coverage]
        F6[Warnings]
        F7[Quick actions]
    end
    
    COMPACT --> COMPACT_REPORT
    FULL --> FULL_REPORT
    
    COMPACT_REPORT --> OUTPUT([📊 Отчёт])
    FULL_REPORT --> OUTPUT
```

---

## 6. Сценарий: Code Review

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant C as 🎯 Claude Code
    participant R as 👀 Review Agent
    participant G as 📂 Git

    U->>C: /review [scope]
    
    Note over C: scope: N commits | staged | branch | all
    
    C->>R: Делегировать review
    
    R->>R: Сброс контекста<br/>(независимый reviewer)
    
    R->>G: git diff [scope]
    G-->>R: Diff changes
    
    R->>R: Automated checks
    Note right of R: npm test<br/>npm run lint<br/>npm run typecheck
    
    R->>R: Security scan
    Note right of R: Secrets detection<br/>Injection patterns<br/>Console statements
    
    R->>R: Deep review<br/>каждого файла
    
    alt Critical issues found
        R-->>C: ❌ REJECTED
        C-->>U: Critical: [issues]
    else Changes requested
        R-->>C: ⚠️ CHANGES REQUESTED
        C-->>U: Fix: [issues]
    else All good
        R-->>C: ✅ APPROVED
        C-->>U: Ready to merge
    end
```

---

## 7. Сценарий: E2E Тестирование

```mermaid
flowchart TD
    START([/test feature/]) --> SETUP[Setup test environment]
    
    SETUP --> START_SERVER{Dev server<br/>needed?}
    START_SERVER -->|Да| RUN_SERVER[npm run dev]
    START_SERVER -->|Нет| UNIT
    RUN_SERVER --> HEALTH[Health check]
    HEALTH --> UNIT
    
    UNIT[Unit Tests] --> UNIT_RESULT{Pass?}
    UNIT_RESULT -->|Нет| UNIT_FAIL[Log failures]
    UNIT_RESULT -->|Да| INTEGRATION
    UNIT_FAIL --> INTEGRATION
    
    INTEGRATION[Integration Tests] --> INT_RESULT{Pass?}
    INT_RESULT -->|Нет| INT_FAIL[Log failures]
    INT_RESULT -->|Да| E2E
    INT_FAIL --> E2E
    
    E2E{E2E method?}
    E2E -->|Playwright| PLAYWRIGHT[Browser automation]
    E2E -->|Manual| CURL[curl API tests]
    
    PLAYWRIGHT --> SCENARIOS
    CURL --> SCENARIOS
    
    SCENARIOS[Test scenarios matrix]
    
    subgraph Matrix[Scenarios]
        S1[Happy path]
        S2[Empty input]
        S3[Invalid input]
        S4[Boundary cases]
        S5[Error handling]
    end
    
    SCENARIOS --> Matrix
    Matrix --> COVERAGE[Coverage check]
    
    COVERAGE --> REPORT[Generate report]
    REPORT --> CLEANUP[Cleanup: stop server]
    CLEANUP --> RESULT{All pass?}
    
    RESULT -->|Да| SUCCESS([✅ PASS])
    RESULT -->|Частично| PARTIAL([⚠️ PARTIAL])
    RESULT -->|Нет| FAIL([❌ FAIL])
    
    style SUCCESS fill:#c8e6c9
    style PARTIAL fill:#fff3e0
    style FAIL fill:#ffcdd2
```

---

## 8. State Diagram: Жизненный цикл задачи

```mermaid
stateDiagram-v2
    [*] --> Backlog: Новая задача
    
    Backlog --> Planning: /plan
    
    Planning --> Planned: План готов
    Planning --> Backlog: Отменено
    
    Planned --> InProgress: /implement
    Planned --> Planning: Требует доработки
    
    InProgress --> Testing: Код готов
    InProgress --> InProgress: TDD итерации
    
    Testing --> InReview: Тесты OK
    Testing --> InProgress: Баги найдены
    
    InReview --> Done: Approved ✅
    InReview --> InProgress: Changes requested
    
    Done --> [*]: Merged
    
    note right of Planning
        Lead Agent + Explore Agent
        Создание плана
    end note
    
    note right of InProgress
        Code Agent
        TDD: Red → Green → Refactor
    end note
    
    note right of Testing
        Test Agent
        Unit + Integration + E2E
    end note
    
    note right of InReview
        Review Agent
        Independent review
    end note
```

---

## 9. Выбор сценария (Decision Tree)

```mermaid
flowchart TD
    START([🤔 Что делать?]) --> TYPE{Тип задачи?}
    
    TYPE -->|Новая фича| SIZE{Размер?}
    SIZE -->|Большая| PLAN[/plan/]
    SIZE -->|Маленькая| QUICK_PLAN[/plan/ краткий]
    
    TYPE -->|Баг| BUG_SIZE{Размер фикса?}
    BUG_SIZE -->|< 20 LOC| QUICK[/quick-fix/]
    BUG_SIZE -->|> 20 LOC| PLAN
    
    TYPE -->|GitHub Issue| ISSUE[/fix-issue N/]
    
    TYPE -->|Проверка| CHECK{Что проверить?}
    CHECK -->|Статус| STATUS[/project-status/]
    CHECK -->|Тесты| TEST[/test/]
    CHECK -->|Код| REVIEW[/review/]
    
    TYPE -->|Исследование| EXPLORE_Q[Задать вопрос в чате<br/>→ Explore Agent]
    
    PLAN --> IMPLEMENT[/implement/]
    QUICK_PLAN --> IMPLEMENT
    
    IMPLEMENT --> TEST
    ISSUE --> REVIEW
    QUICK --> DONE
    
    TEST --> REVIEW
    REVIEW --> DONE([✅ Готово])
    
    style START fill:#e1f5fe
    style DONE fill:#c8e6c9
```

---

## 10. Взаимодействие агентов

```mermaid
flowchart TB
    subgraph User["👤 User Input"]
        CMD[Команда или запрос]
    end
    
    subgraph Router["🎯 Claude Code Router"]
        DETECT{Определить<br/>тип задачи}
    end
    
    subgraph Agents["🤖 Agents"]
        LEAD[🏗️ Lead<br/>Планирование]
        EXPLORE[🔍 Explore<br/>Разведка]
        CODE[💻 Code<br/>Реализация]
        TEST[🧪 Test<br/>Тестирование]
        REVIEW[👀 Review<br/>Проверка]
    end
    
    CMD --> DETECT
    
    DETECT -->|plan, think| LEAD
    DETECT -->|find, search, where| EXPLORE
    DETECT -->|implement, fix, create| CODE
    DETECT -->|test, check, verify| TEST
    DETECT -->|review, audit| REVIEW
    
    LEAD -.->|"Исследовать codebase"| EXPLORE
    LEAD -.->|"Создан план"| CODE
    CODE -.->|"Код готов"| TEST
    TEST -.->|"Тесты OK"| REVIEW
    
    EXPLORE -.->|"Контекст"| LEAD
    EXPLORE -.->|"Контекст"| CODE
    
    style LEAD fill:#e3f2fd
    style EXPLORE fill:#f3e5f5
    style CODE fill:#e8f5e9
    style TEST fill:#fff3e0
    style REVIEW fill:#fce4ec
```

---

## Легенда

| Символ | Значение |
|--------|----------|
| `[...]` | Процесс/Действие |
| `{...}` | Решение/Условие |
| `([...])` | Начало/Конец |
| `-->` | Переход |
| `-.->` | Делегирование/Связь |
| 🔴 | RED (failing test) |
| 🟢 | GREEN (passing test) |
| 🔵 | REFACTOR |
| ✅ | Success |
| ❌ | Failure |
| ⚠️ | Warning |

---

## Как использовать эти схемы

1. **Для обучения** — понять как работает система
2. **Для онбординга** — показать новым членам команды
3. **Для документации** — включить в README проекта
4. **Для отладки** — понять на каком этапе проблема

Схемы в формате Mermaid можно рендерить:
- В GitHub/GitLab README
- В Obsidian, Notion
- На [mermaid.live](https://mermaid.live)
- В VS Code с расширением Mermaid
