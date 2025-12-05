# Architectural Decisions Record (ADR)

## Назначение
Документирование важных архитектурных и дизайн-решений.
Помогает будущим сессиям понять ПОЧЕМУ были сделаны определённые выборы.

## Как использовать
Документируй важные решения по шаблону:
- **Контекст:** Почему возникла необходимость решения?
- **Решение:** Что было выбрано и почему?
- **Альтернативы:** Какие варианты рассматривались?
- **Последствия:** Что станет проще или сложнее?

## Шаблон
```markdown
## [ДАТА] - Название решения

### Статус
[Предложено | Принято | Устарело | Заменено ADR-XXX]

### Контекст
Какая проблема мотивирует это решение?

### Решение
Какое изменение предлагается/делается?

### Рассмотренные альтернативы
1. Альтернатива 1 — почему отклонена
2. Альтернатива 2 — почему отклонена

### Последствия
Что станет проще или сложнее из-за этого решения?

### Ссылки
- Ссылка на issue/PR
- Ссылка на документацию
```

---

## Decisions Log

### 2025-12-04 - Project Structure Setup

**Status:** Accepted

**Context:** 
Need to establish a consistent structure for Claude Code workflow management.

**Decision:**
Use `.claude-workspace/` directory with:
- `progress.md` - session logs
- `features.json` - feature tracking
- `current-task.md` - active task details
- `decisions.md` - this file

**Alternatives Considered:**
1. Single CLAUDE.md file - too cluttered for complex projects
2. GitHub Issues only - no local context between sessions

**Consequences:**
- ✅ Clear separation of concerns
- ✅ Easy to track progress
- ✅ Works offline
- ⚠️ Need to keep files updated

---

### 2025-12-05 - Удаление git reset --hard

**Status:** Accepted

**Context:**
code-agent имел доступ к `git reset --hard` в allowed-tools, что создавало риск потери несохранённого кода.

**Decision:**
Удалить `git reset --hard` из allowed-tools всех агентов. Использовать только безопасные git команды.

**Alternatives Considered:**
1. Оставить с предупреждением — риск всё равно остаётся
2. Добавить подтверждение — невозможно в автоматическом режиме

**Consequences:**
- ✅ Безопаснее, нет риска потери кода
- ✅ Соответствует принципу "не навреди"
- ⚠️ При необходимости hard reset — вручную

---

### 2025-12-05 - Python-first подход для примеров

**Status:** Accepted

**Context:**
Примеры в агентах и командах были на JavaScript/npm, но проект ориентирован на Python.

**Decision:**
Все примеры переписать на Python/pytest. JavaScript оставить как вторичный.

**Alternatives Considered:**
1. Оставить JavaScript — не соответствует целевой аудитории
2. Оба языка равноправно — усложняет документацию

**Consequences:**
- ✅ Консистентность примеров
- ✅ Соответствие Python проектам
- ⚠️ JavaScript разработчикам нужна адаптация

---

### 2025-12-05 - Единый лог сессий

**Status:** Accepted

**Context:**
Существовало два файла логирования: `session-log.txt` и `progress.md`, дублирующих информацию.

**Decision:**
Использовать только `progress.md`, удалить `session-log.txt`.

**Alternatives Considered:**
1. Оставить оба — дублирование, путаница
2. Оставить только session-log.txt — меньше структуры

**Consequences:**
- ✅ Один источник правды
- ✅ Меньше файлов для поддержки
- ✅ progress.md более информативен

---

### 2025-12-05 - Замена security-agent на review-agent

**Status:** Accepted

**Context:**
В lead-agent.md упоминался несуществующий `security-agent` в Delegation Rules.

**Decision:**
Заменить все упоминания `security-agent` на `review-agent`, который включает security проверки.

**Alternatives Considered:**
1. Создать security-agent — избыточно, review-agent уже покрывает
2. Удалить упоминание — теряется security контекст

**Consequences:**
- ✅ Консистентность документации
- ✅ review-agent включает security checks
- ✅ Нет "мёртвых" ссылок

---
