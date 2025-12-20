---
description: Независимый код-ревью недавних изменений. Использовать после /implement, перед /done. Объективная оценка качества.
allowed-tools: Read, Grep, Glob, Bash, Task
---

# /review $ARGUMENTS

Проведи код-ревью как **НЕЗАВИСИМЫЙ** ревьюер.

## Аргументы

| Аргумент | Описание |
|----------|----------|
| `[число]` | Количество коммитов для review |
| `staged` | Только staged changes |
| `branch` | Все коммиты ветки относительно main |
| (пусто) | Auto-detect из state.json |

## ШАГ 1: Context Discovery

```bash
# 1. Текущая задача
cat .claude-workspace/state.json | jq '.currentTask'

# 2. Изменения
git log --oneline -5
git diff --stat HEAD~5 | tail -5
```

## ШАГ 2: Определи scope

```bash
if [ "$ARGUMENTS" = "staged" ]; then
  DIFF_CMD="git diff --cached"
elif [ "$ARGUMENTS" = "branch" ]; then
  BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master)
  DIFF_CMD="git diff $BASE..HEAD"
elif [ -n "$ARGUMENTS" ]; then
  DIFF_CMD="git diff HEAD~$ARGUMENTS"
else
  # Auto: коммиты с начала задачи
  DIFF_CMD="git diff HEAD~5"
fi
```

## ШАГ 3: Автоматические проверки

```bash
# Тесты
npm test 2>&1 | tail -20 || pytest -v 2>&1 | tail -20

# Linting
npm run lint 2>&1 | head -30 || ruff check . 2>&1 | head -30

# Type checking
npm run typecheck 2>&1 | head -20 || mypy . 2>&1 | head -20
```

## ШАГ 4: Проверка безопасности

```bash
# Secrets
rg -i "(api[_-]?key|password|secret|token).*[=:].*['\"][^'\"]{8,}" --type py --type ts | head -10

# Console/print в production
rg "(console\.(log|debug)|print\()" --type py --type ts | grep -v test | head -10
```

## ШАГ 5: Детальный обзор

Для каждого файла:
- Читай как будто видишь **впервые**
- Проверяй логику (mental trace)
- Ищи edge cases

## Чеклист

### Корректность ✓
- [ ] Соответствует плану из state.json
- [ ] Логика корректна
- [ ] Edge cases обработаны
- [ ] Error handling присутствует

### Качество кода ✓
- [ ] Читаемый код
- [ ] Понятные имена
- [ ] Нет дублирования (DRY)
- [ ] Функции < 50 строк

### Тестирование ✓
- [ ] Тесты для новой функциональности
- [ ] Happy path покрыт
- [ ] Edge/error cases покрыты
- [ ] Тесты независимы

### Безопасность ✓
- [ ] Нет hardcoded secrets
- [ ] Input validation
- [ ] Нет SQL/XSS injection

## Auto-REJECT критерии

| Находка | Действие |
|---------|----------|
| Hardcoded secrets | ❌ REJECT |
| SQL/Command injection | ❌ REJECT |
| console.log в production | ⚠️ CHANGES REQUESTED |
| Нет тестов | ⚠️ CHANGES REQUESTED |

## Формат вывода

```markdown
## Code Review

**Scope:** [что проверено]
**Verdict:** ✅ APPROVED | ⚠️ CHANGES REQUESTED | ❌ REJECTED
**Quality:** ⭐⭐⭐⭐☆ (4/5)

### Автоматические проверки

| Check | Status |
|-------|--------|
| Tests | ✅/❌ |
| Lint | ✅/❌ |
| Types | ✅/❌ |
| Security | ✅/⚠️/❌ |

### Findings

#### 🔴 Critical (must fix)
1. **[Title]** — `file:line` — [issue] — [solution]

#### 🟠 High (should fix)
1. ...

#### 🟡 Medium (consider)
1. ...

### What's Good ✅
- [positive 1]
- [positive 2]

### Next Steps

При APPROVED:
> Код одобрен. Запустите `/done` для завершения задачи.

При CHANGES REQUESTED:
> Исправьте findings и запустите `/review` повторно.
```

## После ревью

**Обновить state.json:**
- currentTask.status = "review"
- Добавить в progress[]: type = "REVIEW", message = verdict

## Правила

- Будь **объективен** — хвали хорошее, указывай на плохое
- Объясняй **ПОЧЕМУ** что-то плохо
- Предлагай **конкретные решения**
- **Приоритизируй** — не придирайся к мелочам
