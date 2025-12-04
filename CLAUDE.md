# Project: Claude-Code-Kit

## Overview
Шаблон и справочник для эффективной работы с Claude Code. Содержит структуру проекта, slash commands, agent prompts и best practices на основе рекомендаций Anthropic.

## Tech Stack
- Type: Template/Documentation project
- Format: Markdown, JSON

## Commands
- No build/test commands (documentation project)
- Git workflow as usual

## Code Style
- Markdown files: use consistent headers and formatting
- JSON files: 2-space indentation
- Keep documentation concise and actionable

## Project Structure
- `CLAUDE.md` - Main project context (this file)
- `.claude/commands/` - Slash commands for Claude Code
- `.claude-workspace/` - Working files for tracking progress
- `docs/agents/` - Agent prompts (Lead, Code, Review, Test)
- `claude-code-project-structure.md` - Full reference documentation

## Workflow Rules
1. ALWAYS read `.claude-workspace/progress.md` at session start
2. ALWAYS update progress.md after completing work
3. Work on ONE task at a time
4. Document architectural decisions in `.claude-workspace/decisions.md`

## Available Slash Commands
- `/project:init-project` - Initialize new project for Claude Code
- `/project:plan [feature]` - Create implementation plan
- `/project:implement` - Implement current task
- `/project:review [commits]` - Code review
- `/project:test [feature]` - Test feature E2E
- `/project:fix-issue [#]` - Fix GitHub issue
- `/project:status` - Show project status

## Do Not
- Do NOT delete files from .claude-workspace/ without archiving
- Do NOT skip progress.md updates
- Do NOT modify agent prompts without discussion
