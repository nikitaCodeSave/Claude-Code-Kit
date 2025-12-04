# Project: Claude Code Kit

## Overview
A template/toolkit project that provides structure, agents, and slash commands for efficient Claude Code workflows. This project is designed to be copied and adapted for new projects.

## Tech Stack
- Documentation: Markdown
- Configuration: JSON
- Shell scripts for hooks
- Git for version control

## Project Structure
- `.claude/` - Claude Code configuration
  - `agents/` - Agent prompts (lead, code, review, test, explore, doc)
  - `commands/` - Slash commands (plan, implement, review, test, etc.)
  - `hooks/` - Shell hooks (validate-bash.sh)
  - `settings.local.json` - Local settings
- `.claude-workspace/` - Working files for tracking
  - `progress.md` - Session logs
  - `features.json` - Feature tracking
  - `current-task.md` - Active task details
  - `decisions.md` - Architectural decisions
- `docs/` - Documentation

## Commands
- `/init-project` - Initialize a new project with Claude Code structure
- `/plan [feature]` - Create a detailed implementation plan
- `/implement` - Implement current task from plan
- `/review` - Independent code review of changes
- `/test [feature]` - End-to-end testing
- `/quick-fix [bug]` - Quick fix for small bugs
- `/status` - Check project status

## Agents
- **lead-agent** - Planning and task decomposition
- **code-agent** - TDD implementation
- **review-agent** - Independent code review
- **test-agent** - QA and testing
- **explore-agent** - Codebase exploration
- **doc-agent** - Documentation

## Workflow Rules
1. ALWAYS read `.claude-workspace/progress.md` at session start
2. ALWAYS update progress.md after completing work
3. Work on ONE feature at a time
4. Use `/plan` before implementing any feature > 50 LOC
5. Use `/review` after implementation completion

## Git Conventions
- Commit format: `type(scope): description`
- Types: feat, fix, docs, chore, refactor

## Important Notes
- This is a template project - copy and adapt for your needs
- All agents use OODA loop methodology
- TDD workflow is enforced (tests before code)
