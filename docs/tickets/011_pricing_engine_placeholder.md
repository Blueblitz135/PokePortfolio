# Ticket 011 - Pricing Engine Placeholder

## Goal

Add manual price snapshots before real external pricing.

## Requirements

- Add endpoint to create manual price snapshot.
- Show latest price snapshot on asset detail.
- Use latest price in calculations.
- Source should be `manual`.
- Confidence can default to 0.5.

## Endpoint

```http
POST /api/assets/{asset_id}/price-snapshots
```

## Acceptance criteria

- User can set manual market price per unit.
- Calculations update using latest price snapshot.
- Frontend displays market value, profit/loss, and ROI.
- CAD is default.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/05_pricing_engine.md, and docs/tickets/011_pricing_engine_placeholder.md.
Implement manual price snapshots only.
Do not implement external pricing adapters.
```
