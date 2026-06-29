# Ticket 012 - Currency Layer

## Goal

Add currency structure with CAD default and future conversion support.

## Requirements

- CAD is default app currency.
- Add currency fields where needed.
- Add basic currency service interface.
- Add display currency dropdown placeholder in frontend if easy.
- Do not overbuild historical FX.

## Acceptance criteria

- Purchase lots default to CAD.
- Price snapshots default to CAD.
- API responses include currency.
- Code has a clear place to add live FX conversion later.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/07_currency_strategy.md, and docs/tickets/012_currency_layer.md.
Implement the currency layer structure with CAD default.
Keep it simple.
```
