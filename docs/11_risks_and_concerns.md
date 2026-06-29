# 11 - Risks and Concerns

## 1. Sealed product images are not fully solved

Free APIs may not consistently provide sealed product images. MVP should use user uploads and placeholders.

Future fix:

- build a curated sealed product table
- allow admin/user uploads
- use external images only where licensing/terms are acceptable

## 2. Graded pricing is not solved by card metadata APIs

TCGdex and Pokémon TCG API are card metadata/image APIs. They do not fully solve PSA/BGS/CGC market pricing.

Future fix:

- eBay sold comps
- auction data
- third-party market APIs
- manual price snapshots

## 3. Raw card condition is noisy

Raw card pricing depends heavily on condition, but seller-reported conditions are inconsistent.

Future fix:

- price NM/LP/MP/DMG separately
- reduce confidence for unclear condition
- use image analysis later if feasible

## 4. eBay data requires filtering

Even sold/completed comps can contain relists, unpaid/cancelled items, weird bundles, and outliers.

Future fix:

- title normalization
- exact identity matching
- remove suspicious prices
- remove listings with bundle keywords
- calculate confidence from clean sample size

## 5. Pack art-specific valuation is intentionally excluded

Booster pack art and ETB/tin artwork versions can matter, but many listings do not specify them clearly.

MVP rule:

- do not track pack art
- do not track ETB/tin artwork versions

Future fix:

- add optional artwork version field
- only use it when data quality is good

## 6. Currency consistency

Market data may appear in USD, CAD, EUR, GBP, or JPY. Portfolio calculations must not mix currencies.

MVP rule:

- CAD default
- convert external prices to CAD before calculations

## 7. AI assistant should come late

The AI assistant is only useful after the app has clean structured data and market prices.

Do not build it before:

- assets work
- purchase lots work
- images work
- price snapshots work
- calculations work
