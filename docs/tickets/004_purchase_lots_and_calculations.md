# Ticket 004 - Purchase Lots and Calculations

## Goal

Allow the user to add multiple purchase records for the same asset and calculate portfolio values.

## Endpoints

- POST /api/assets/{asset_id}/purchase-lots
- PATCH /api/purchase-lots/{lot_id}
- DELETE /api/purchase-lots/{lot_id}

## Calculation service

For each asset, calculate:

- total quantity
- total cost
- average cost per unit
- market price per unit if available
- total market value if available
- profit/loss if available
- ROI percentage if available

## Rules

- No taxes.
- No fees.
- No shipping.
- No purchase source.
- Quantity comes from lots.

## Acceptance criteria

- User can add multiple lots to one asset.
- User can edit each lot.
- User can delete each lot.
- Asset detail API returns summarized totals.
- Market fields are null if no price snapshot exists.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/02_data_model.md, docs/03_api_contract.md, and docs/tickets/004_purchase_lots_and_calculations.md.
Implement purchase lot endpoints and calculation service.
Add tests for calculation logic.
```
