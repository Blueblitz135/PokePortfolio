# Ticket 014 - External Pricing Adapters

## Goal

Start adding real pricing adapters after the app works manually.

## Order

1. JustTCG adapter if useful for raw card pricing.
2. Pokémon TCG API price fields if useful.
3. TCGdex metadata remains card identity/image source.
4. eBay sold comps later with careful filtering.

## Requirements

- Keep adapters isolated.
- Do not let external APIs infect core data model.
- Normalize all prices to CAD.
- Store results as PriceSnapshot.
- Include confidence.

## Acceptance criteria

- Adapter can be called independently.
- Adapter output is normalized.
- Failures do not crash the app.
- Price snapshots can be created from adapter output.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/05_pricing_engine.md, docs/08_external_api_decision.md, and docs/tickets/014_external_pricing_adapters.md.
Implement one external pricing adapter only.
Start with the simplest useful adapter.
Keep it isolated and tested.
```
