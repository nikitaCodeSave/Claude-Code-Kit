---
description: Initializes project workspace for Claude Code. Creates tracking files, workspace structure, and validates configuration. Run once at project start.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
# Initialize Project for Claude Code

Инициализируй проект для эффективной работы с Claude Code.

## Process

### 1. Analyze Project

```bash
# Определи тип проекта
echo "=== Project Analysis ==="
ls -la

# Tech stack
if [ -f "package.json" ]; then
  echo "Node.js project detected"
  cat package.json | jq '.name, .scripts'
elif [ -f "pyproject.toml" ]; then
  echo "Python project detected"
  cat pyproject.toml | head -20
elif [ -f "Cargo.toml" ]; then
  echo "Rust project detected"
elif [ -f "go.mod" ]; then
  echo "Go project detected"
else
  echo "Unknown project type"
fi

# Existing Claude config
if [ -d ".claude" ]; then
  echo "Existing .claude/ directory found"
  ls -la .claude/
fi
```

### 2. Create Workspace Structure

```bash
# Create directories
mkdir -p .claude-workspace
mkdir -p .claude/commands
mkdir -p .claude/agents
mkdir -p .claude/hooks
```

### 3. Create Tracking Files

#### .claude-workspace/progress.md
```markdown
# Progress Log

## How to Use
- Add entry at START of each session with task
- Add entry at END of each session with results
- Keep last 20 sessions, archive older

---

## Session: [YYYY-MM-DD HH:MM]
**Task:** Project initialization
**Completed:**
- Created .claude-workspace structure
- Initialized tracking files
**Notes:** Ready for development

---
```

#### .claude-workspace/features.json
```json
{
  "project": "[PROJECT_NAME]",
  "lastUpdated": "[ISO_DATE]",
  "features": []
}
```

#### .claude-workspace/current-task.md
```markdown
# Current Task

No active task.

Use `/project:plan [feature]` to start planning a new feature.
```

#### .claude-workspace/decisions.md
```markdown
# Architectural Decisions

## How to Use
Document important decisions with:
- **Context:** Why was this decision needed?
- **Decision:** What was decided?
- **Consequences:** What are the implications?

---

## [DATE] - Project Initialization

**Context:** Setting up Claude Code workflow for this project.

**Decision:** Using standard .claude-workspace structure with TDD workflow.

**Consequences:** All team members will follow consistent development process.

---
```

### 4. Create/Update CLAUDE.md

If CLAUDE.md doesn't exist, create basic one:

```markdown
# Project: [NAME]

## Tech Stack
- [detected tech stack]

## Commands
- `npm run dev` — start dev server
- `npm test` — run tests
- `npm run lint` — run linter

## Code Style
- [auto-detect from config files]

## Architecture
- [brief description]

## Important Notes
- [any critical info]
```

### 5. Validate Settings

```bash
# Check for hooks configuration
if [ ! -f ".claude/settings.json" ] && [ ! -f ".claude/settings.local.json" ]; then
  echo "No hooks configured. Consider adding .claude/settings.json"
fi

# Check for agents
if [ -z "$(ls -A .claude/agents/ 2>/dev/null)" ]; then
  echo "No custom agents. Consider adding agents to .claude/agents/"
fi
```

### 6. Git Setup

```bash
# Add to .gitignore if needed
if ! grep -q "CLAUDE.local.md" .gitignore 2>/dev/null; then
  echo "" >> .gitignore
  echo "# Claude Code local files" >> .gitignore
  echo "CLAUDE.local.md" >> .gitignore
  echo ".claude/settings.local.json" >> .gitignore
  echo ".claude-workspace/session-log.txt" >> .gitignore
fi

# Initial commit
git add .claude-workspace/
git add .claude/
git add CLAUDE.md
git add .gitignore
git commit -m "chore: initialize Claude Code workspace"
```

## Output

```markdown
## ✅ Project Initialized for Claude Code

### Created Structure
```
.claude-workspace/
├── progress.md      ✅
├── features.json    ✅
├── current-task.md  ✅
└── decisions.md     ✅

.claude/
├── agents/          [X agents]
├── commands/        [X commands]
├── hooks/           [configured/not configured]
└── settings.json    [exists/missing]
```

### CLAUDE.md
[Created/Updated/Already exists and valid]

### Git
[Initial commit created / Already tracked]

---

### 🚀 Next Steps

1. Review and customize `CLAUDE.md` for your project
2. Run `/project:status` to see current state
3. Run `/project:plan [first feature]` to start development

### 💡 Recommended Commands
- `/project:status` — check project state
- `/project:plan [feature]` — plan a new feature
- `/project:quick-fix [bug]` — fix small bugs
```