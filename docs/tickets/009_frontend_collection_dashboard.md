# Ticket 009 - Frontend Collection Dashboard

## Goal

Build the main collection dashboard UI.

## Page

```txt
/collection
```

## Display fields

- image
- display name
- asset type
- total quantity
- average cost
- latest market price if available
- total market value if available
- profit/loss if available
- ROI if available

## Actions

- add new asset
- open asset detail
- filter by asset type

## Acceptance criteria

- Dashboard loads assets from backend.
- Empty state is clear.
- Cards/raw/graded/sealed display properly.
- Market fields handle null values gracefully.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/04_frontend_pages.md, and docs/tickets/009_frontend_collection_dashboard.md.
Implement the collection dashboard.
Use simple styling and readable components.
```
