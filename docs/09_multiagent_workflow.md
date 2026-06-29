# 09 - Multiagent Workflow

## Main rule

Do not start with many agents editing the same files. That creates conflicts.

Start with one VS Code Codex agent and one ticket at a time. Add multiagent workflows only after the repo has:

- Git initialized
- backend running
- frontend running
- database models created
- tests/checks available
- clear tickets

## Recommended tools

### VS Code Codex agent

Use for your main coding loop:

- edit files
- run tests
- fix bugs
- explain code
- implement one ticket at a time

### Standalone Codex app

Use later for parallel work:

- one agent on backend branch
- one agent on frontend branch
- one agent reviewing diffs
- experiments you may discard

## Single-agent workflow first

For tickets 001 to 005, use only one agent.

Workflow:

```txt
1. git status
2. choose one ticket
3. paste ticket prompt into VS Code Codex
4. let Codex edit files
5. run app/tests
6. manually review diff
7. ask Codex to fix only ticket-related issues
8. commit
9. move to next ticket
```

## Safe multiagent workflow

After ticket 005, you can use separate branches.

Example branches:

```txt
main
feature/backend-card-search
feature/frontend-asset-detail
feature/review-cleanup
```

## Agent roles

### Agent A - Planner

Purpose:

- reads docs
- creates tickets
- does not edit code

Prompt:

```txt
You are the planner agent.
Read docs/ and tickets/.
Create or refine the next 3 implementation tickets.
Do not edit application code.
Each ticket must include goal, files affected, acceptance criteria, and tests.
```

### Agent B - Backend Builder

Purpose:

- backend only
- database models
- API routes
- services
- tests

Prompt:

```txt
You are the backend builder agent.
Read AGENTS.md, CODING_RULES.md, and the assigned ticket.
Only edit backend files unless the ticket explicitly requires otherwise.
Implement the ticket with minimal changes.
Run backend tests/checks.
Summarize changed files.
```

### Agent C - Frontend Builder

Purpose:

- frontend only
- React components
- pages
- API client

Prompt:

```txt
You are the frontend builder agent.
Read AGENTS.md, CODING_RULES.md, docs/04_frontend_pages.md, docs/03_api_contract.md, and the assigned ticket.
Only edit frontend files unless the ticket explicitly requires otherwise.
Implement the ticket with simple React + TypeScript components.
Run frontend checks.
Summarize changed files.
```

### Agent D - Reviewer

Purpose:

- inspect changes
- fix bugs only
- no new features

Prompt:

```txt
You are the reviewer agent.
Review the uncommitted changes against the assigned ticket.
Check for missing acceptance criteria, bugs, bad naming, unnecessary complexity, and broken tests.
Do not add new features.
Only propose or make fixes directly related to the ticket.
```

## How to run multiagent practically

### Option 1: VS Code only

Use one agent at a time. This is safest for beginners.

### Option 2: Standalone Codex app with branches

1. Create a clean branch for one task.
2. Open that branch/worktree in the Codex app.
3. Assign only one ticket to that agent.
4. Use a different branch/worktree for a different agent.
5. Merge only after review.

### Option 3: Subagents

Use subagents only when the task can be clearly split.

Good subagent tasks:

- one subagent reviews backend API
- one subagent reviews frontend UI
- one subagent checks tests

Bad subagent tasks:

- three agents all editing the same asset detail page
- multiple agents changing database schema at once

## First time multiagent example

After tickets 001-005 are complete:

```txt
Ask one agent to implement backend card metadata search.
Ask another agent to implement frontend card search UI.
Ask reviewer agent to check both after you merge locally.
```

Do not run parallel agents on database schema changes.
