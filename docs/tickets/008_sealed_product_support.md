# Ticket 008 - Sealed Product Support

## Goal

Make sealed products first-class assets in the frontend and backend.

## Supported sealed product types

- booster_box
- booster_pack
- elite_trainer_box
- booster_bundle
- tin
- collection_box
- other

## Rules

- Booster bundle always has 6 packs.
- Do not track pack art.
- Do not track ETB artwork version.
- Do not track tin artwork version.
- User-uploaded image is primary sealed image source.
- Placeholder image is used when no image exists.

## Acceptance criteria

- User can create sealed product asset.
- User can select sealed product type.
- User can add purchase lots.
- Asset detail calculations work for sealed products.
- Image upload works for sealed products.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/02_data_model.md, docs/06_image_strategy.md, and docs/tickets/008_sealed_product_support.md.
Implement sealed product support across backend and frontend where needed.
Respect all MVP exclusions.
```
