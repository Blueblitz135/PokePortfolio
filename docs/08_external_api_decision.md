# 08 - External API Decision

## Main question

Which free API should the app use for raw cards, graded cards, and sealed products?

Candidates:

- TCGdex
- Pokémon TCG API
- JustTCG

## Recommendation summary

Use this split:

```txt
Card metadata/images: TCGdex primary
Card metadata/image fallback: Pokémon TCG API
Raw card pricing: JustTCG optional adapter if feasible
Graded card pricing: not solved by these APIs
Sealed product pricing/images: not fully solved by these APIs
```

## TCGdex

Best use:

- card metadata
- card images
- set data
- card number/set total
- clean Pokémon card identity

Use it first for search and images.

## Pokémon TCG API

Best use:

- fallback card metadata
- card images
- card number and set totals
- possible TCGplayer/Cardmarket fields where available

Use it as a fallback if TCGdex does not return enough data.

## JustTCG

Best use:

- possible card pricing data
- raw card variants/conditions if supported by available plan

Use it later as a pricing adapter, not as the primary image source.

## Graded card issue

Graded card pricing is not fully solved by TCGdex, Pokémon TCG API, or JustTCG.

MVP solution:

- store graded card metadata manually
- use card image + grade overlay
- allow manual market price snapshot

Future solution:

- eBay sold comps
- auction archives
- grading-company APIs if available
- third-party market data if affordable

## Sealed product issue

Sealed product metadata, pricing, and images are not consistently solved by the three unpaid APIs.

MVP solution:

- let user add sealed products manually
- use upload-first image flow
- allow manual market price snapshot

Future solution:

- curated sealed product database
- external sealed product endpoint if available
- eBay sold comps with strict title matching

## Final decision for MVP

Implement in this order:

1. Manual asset creation for all asset types.
2. Image uploads for all asset types.
3. TCGdex card metadata search.
4. Pokémon TCG API fallback.
5. Manual price snapshots.
6. JustTCG pricing adapter.
7. eBay/auction adapters later.
