# Development Workflow

## Atomic Tasks
Development is strictly divided into Atomic Tasks (e.g., AT-001, AT-002).
Each task is an independent unit of work with:
- Objective
- Files to create/modify
- Acceptance Criteria

**Rules:**
- Only implement one Atomic Task at a time.
- Never continue automatically; await explicit approval before proceeding to the next task.

## AI Collaboration Workflow
When pairing with AI coding assistants:
1. Provide the Atomic Task details.
2. The AI must explain the implementation approach.
3. The AI must list every file modified or created.
4. The AI must provide clear instructions on how to test the changes locally.
5. The AI must pause and wait for user approval.

## Git Workflow & Branch Strategy
- **Main Branch**: The `main` branch is the single source of truth and must always be deployable.
- **Feature Branches**: All development occurs on short-lived feature branches derived from `main`.
- **Commits**: Commits should be atomic, descriptive, and reference the Atomic Task.

## Testing Expectations
- **Unit Tests**: Required for all business logic, indicators, and core abstractions.
- **Test Location**: All tests reside in the `tests/` directory mirroring the `atlas/` structure.
- **Execution**: Run tests to verify logic before proposing any changes or concluding a task.

## Code Review Checklist
- [ ] Does the code adhere to the Clean Architecture boundaries?
- [ ] Are type hints comprehensive and accurate?
- [ ] Do public methods and classes have descriptive docstrings?
- [ ] Is there sufficient unit test coverage for new logic?
- [ ] Does the code follow the Single Responsibility Principle?
- [ ] Are there any hardcoded paths or credentials? (There should be none).

## Naming Conventions
- **Files/Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Interfaces/Base Classes**: Often prefixed with `Base` (e.g., `BaseProvider`).

## Documentation Standards
- All architectural decisions must be recorded as an ADR (Architecture Decision Record) in `docs/adr/`.
- Markdown is the standard format for all documentation.
- Maintain clear headings, use tables for structured data, and include ASCII diagrams where useful.
- Ensure documentation reflects the *current* state of the project, not future features.
