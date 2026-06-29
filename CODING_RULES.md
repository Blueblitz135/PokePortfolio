# Coding Rules

This file repeats the most important rules in plain language. `AGENTS.md` is the main Codex instruction file, but this file is useful for quick reference.

## Build style

- Build one ticket at a time.
- Keep changes small.
- Prefer readable code.
- Do not add external APIs before the basic collection app works.
- Do not add AI before pricing and portfolio data exist.

## Product logic

- Assets are things that exist in the market: cards and sealed products.
- Purchase lots are the user's ownership records.
- Quantity belongs to purchase lots.
- Total quantity is the sum of purchase lot quantities.
- Total cost is the sum of purchase lot quantity multiplied by purchase price per unit.
- Average cost is total cost divided by total quantity.
- Market value is market price per unit multiplied by total quantity.
- Profit/loss is market value minus total cost.
- ROI percentage is profit/loss divided by total cost.

## Card identifiers

A card should be identified by:

- name
- set name
- year if available
- card number
- set total
- variant/printing if relevant
- raw condition or grade, depending on asset type

Example: Umbreon VMAX `215/203` should not have `215/203` forced into the title. It should be searchable as structured metadata.

## MVP exclusions

Do not implement these in MVP unless a later ticket asks:

- taxes
- shipping
- seller/source
- fees
- pack art-specific values
- ETB artwork version-specific values
- tin artwork version-specific values
- auto bidding
- scraping
- AI assistant
- alerts
- authentication
