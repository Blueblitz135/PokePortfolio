# Ticket 003 - Manual Collection CRUD

## Goal

Allow the app to create, list, view, update, and delete assets manually.

## Endpoints

- POST /api/assets
- GET /api/assets
- GET /api/assets/{asset_id}
- PATCH /api/assets/{asset_id}
- DELETE /api/assets/{asset_id}

## Requirements

Support creating:

- raw card assets
- graded card assets
- sealed product assets

## Acceptance criteria

- User can create raw card asset.
- User can create graded card asset.
- User can create sealed product asset.
- User can list all assets.
- User can view one asset.
- User can update asset note/display name.
- User can delete asset.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/03_api_contract.md, and docs/tickets/003_manual_collection_crud.md.
Implement backend manual asset CRUD only.
Do not implement purchase lots yet unless needed for schema relationships.
```
