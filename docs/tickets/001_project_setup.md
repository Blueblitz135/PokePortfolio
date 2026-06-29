# Ticket 001 - Project Setup

## Goal

Create the initial full-stack project structure.

## Scope

Use:

- FastAPI backend
- React + Vite + TypeScript frontend
- PostgreSQL-ready database setup
- SQLite fallback allowed for local MVP if needed

## Requirements

Create a structure like:

```txt
backend/
  app/
    main.py
    config.py
    api/
    models/
    schemas/
    services/
    db/
    tests/
frontend/
  src/
    components/
    pages/
    api/
    types/
```

Add basic health endpoint:

```http
GET /api/health
```

Expected response:

```json
{"status": "ok"}
```

## Do not implement

- external APIs
- pricing
- AI
- auth
- alerts
- scraping

## Acceptance criteria

- Backend can start.
- Frontend can start.
- Health endpoint works.
- README includes local setup commands.
- Git diff is small and focused.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, and docs/tickets/001_project_setup.md.
Implement this ticket only.
After coding, run available checks and summarize changed files.
```
