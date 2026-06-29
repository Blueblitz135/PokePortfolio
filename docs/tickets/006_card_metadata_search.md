# Ticket 006 - Card Metadata Search

## Goal

Add card metadata search using TCGdex as the primary adapter.

## Endpoint

```http
GET /api/search/cards?q=
```

## Return fields

- external source
- external id
- card name
- set name
- set id
- year if available
- card number
- set total
- rarity
- image URL

## Rules

- Do not implement pricing here.
- Do not create assets automatically unless user confirms in frontend later.
- Pokémon TCG API fallback can be added in this ticket only if simple; otherwise leave TODO.

## Acceptance criteria

- Search endpoint returns normalized card results.
- Results include card number and set total when available.
- Results include image URL when available.
- Backend handles no results gracefully.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/08_external_api_decision.md, and docs/tickets/006_card_metadata_search.md.
Implement TCGdex card metadata search adapter and backend endpoint.
Do not implement pricing.
```
