# Ticket 002 - Database Models

## Goal

Implement core database models and Pydantic schemas.

## Models

- Asset
- CardMetadata
- RawCardDetails
- GradedCardDetails
- SealedProductMetadata
- PurchaseLot
- AssetImage
- PriceSnapshot

## Important rules

- Quantity belongs to PurchaseLot, not Asset.
- Asset supports raw_card, graded_card, sealed_product.
- Card number and set total are structured fields.
- CAD is default currency.
- Sealed product pack art is not modeled for MVP.

## Acceptance criteria

- Models exist.
- Schemas exist.
- Database can create tables/migrations depending on stack.
- Basic tests or smoke check passes.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/02_data_model.md, and docs/tickets/002_database_models.md.
Implement the database models and schemas only.
Do not implement frontend or external APIs.
```
