# 05 - Pricing Engine

## MVP pricing approach

MVP should use manual price snapshots first.

Reason: external pricing is difficult because raw, graded, and sealed products each require different matching and filtering logic.

## Pricing separation rule

Never mix these in the same pricing calculation:

- raw card NM
- raw card LP
- raw card MP
- raw card DMG
- PSA 10
- PSA 9
- BGS 9.5
- sealed booster box
- sealed booster pack
- sealed ETB

Each distinct asset identity should have its own price snapshots.

## Future pricing sources

### Card metadata APIs

TCGdex and Pokémon TCG API are useful for card identity and images, not complete investment pricing.

### JustTCG

Potentially useful for raw card pricing variants and market prices, but should be treated as an adapter with limitations.

### eBay sold listings

Useful for comps, but needs careful filtering:

- remove relists
- remove suspicious prices
- handle unpaid/cancelled sales risk
- normalize titles
- convert currency to CAD
- avoid active asking prices as market value

The confidence for eBay sold comps should be moderate-to-high when enough clean sales exist, but not perfect.

### Fanatics/PWCC or auction archives

Potentially useful for graded cards, but may require scraping or paid access. Not MVP.

## Future blended pricing algorithm

Suggested process:

1. Fetch candidate sales/listings.
2. Normalize title and metadata.
3. Match to exact asset identity.
4. Remove invalid or suspicious rows.
5. Convert all prices to CAD.
6. Apply source weighting.
7. Apply time decay.
8. Calculate estimated price, range, sales count, and confidence.

## Suggested output

```json
{
  "asset_id": 123,
  "estimated_price_per_unit": 850.00,
  "currency": "CAD",
  "range_low": 790.00,
  "range_high": 920.00,
  "sales_count": 18,
  "confidence": 0.78,
  "source_breakdown": {
    "manual": 0,
    "justtcg": 4,
    "ebay": 14
  }
}
```

## Confidence factors

Increase confidence when:

- more sales exist
- sales are recent
- prices are tightly clustered
- exact match is strong
- source is reliable

Decrease confidence when:

- few comps exist
- titles are ambiguous
- large price spread exists
- raw condition is unclear
- sealed product variation is unclear
- currency conversion was required
