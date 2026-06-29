# Ticket 013 - Tests and Quality

## Goal

Add basic tests and quality checks before external integrations.

## Backend tests

Test:

- asset creation
- purchase lot creation
- calculation service
- price snapshot logic
- image validation if feasible

## Frontend checks

Add or run:

- TypeScript check
- lint if configured
- basic component sanity checks if feasible

## Acceptance criteria

- Backend tests pass.
- Frontend type check passes.
- README documents test commands.
- Reviewer agent can use this as a baseline.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, and docs/tickets/013_tests_and_quality.md.
Add meaningful tests and quality checks for existing functionality.
Do not add new product features.
```
