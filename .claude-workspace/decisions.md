# Architectural Decisions Record (ADR)

## Purpose
Document important architectural and design decisions.
This helps future sessions understand WHY certain choices were made.

## Template
```markdown
## [DATE] - Decision Title

### Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

### Context
What is the issue that we're seeing that is motivating this decision?

### Decision
What is the change that we're proposing and/or doing?

### Alternatives Considered
1. Alternative 1 - why rejected
2. Alternative 2 - why rejected

### Consequences
What becomes easier or more difficult because of this decision?

### References
- Link to related issue/PR
- Link to documentation
```

---

## Decisions Log

### [DATE] - Project Structure Setup

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
