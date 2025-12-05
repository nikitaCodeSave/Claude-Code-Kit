# Current Task

No active task. 

## Quick Start
1. Run `/plan [feature name]` to create a plan
2. After plan is approved, run `/implement`
3. Run `/review` to verify changes
4. Run `/test [feature]` for E2E testing

## Task Template
When a task is active, this file will contain:

```markdown
## Task: [Feature Name]

### Objective
[Clear goal in 1-2 sentences]

### Scope
**In Scope:**
- Item 1
- Item 2

**Out of Scope:**
- Item 1

### Implementation Steps
1. [ ] Step 1 - description
2. [ ] Step 2 - description
3. [ ] Step 3 - description
4. [ ] Write tests
5. [ ] Update documentation

### Files to Modify
- `path/to/file.py` - reason for change

### Files to Create
- `path/to/new.py` - purpose

### Dependencies
- package-name: reason

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All tests pass
- [ ] No linting errors

### Risks
- Risk 1: mitigation strategy

### Notes
[Any additional context]
```
