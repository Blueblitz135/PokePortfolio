# AGENTS.md

These are project instructions for Codex. Read this before making changes.

## Project identity

This project is a Pokémon portfolio investment app. It tracks raw cards, graded cards, and sealed Pokémon products. The app should let a user record what they bought, when they bought it, what they paid, how many units they own, what the current market value is, and how their collection is performing.

## Core product rules

- Do not build features outside the current ticket.
- Build in small, reviewable steps.
- Keep the app beginner-readable and maintainable.
- Prioritize a working MVP over clever architecture.
- Raw cards, graded cards, and sealed products must not be mixed in pricing calculations.
- Quantity belongs to user purchase records, not to the asset metadata itself.
- A user can have multiple purchase lots for the same asset.
- Purchase lots include purchase date, quantity, and purchase price per unit.
- No taxes, fees, seller/source, or shipping fields are required for MVP.
- Each asset can have an optional overall user note.
- Default currency is CAD.
- If external prices are returned in another currency, convert to CAD before storing normalized values.
- Users may later change display currency from a dropdown, but internal normalized market values should be consistent.
- Card number such as `215/203` must be stored as structured identifiers: `card_number = "215"`, `set_total = "203"` or equivalent. Do not force it into the title.
- Pack art is not tracked for MVP.
- Booster bundles always have 6 packs and do not need a `pack_count` property.

## Asset types

Use these asset type values unless a ticket says otherwise:

```txt
raw_card
graded_card
sealed_product
```

Use these sealed product type values:

```txt
booster_box
booster_pack
elite_trainer_box
booster_bundle
tin
collection_box
other
```

## Backend rules

- Use FastAPI.
- Use Pydantic schemas for request and response objects.
- Keep API routes thin.
- Put business logic in services.
- Put database models in a models module.
- Use clear names: `Asset`, `CardMetadata`, `SealedProductMetadata`, `PurchaseLot`, `AssetImage`, `PriceSnapshot`.
- Prefer SQLAlchemy or SQLModel if database setup is required.
- Use PostgreSQL-ready code, but SQLite fallback for local development is acceptable during MVP.
- Add tests for business logic when reasonable.

## Frontend rules

- Use React + TypeScript.
- Use simple, readable components.
- Keep page-level components separate from reusable components.
- Do not spend too much time on advanced styling until core functionality works.
- Show clear loading, empty, and error states.

## External API rules

- TCGdex should be the primary card metadata and image source for cards.
- Pokémon TCG API can be a fallback for card metadata/images.
- JustTCG can be treated as an optional pricing/market adapter, especially for raw card variants, if feasible.
- None of those APIs fully solves graded card pricing or sealed product pricing by itself.
- Do not scrape or implement eBay until a later ticket explicitly asks for it.

## Image rules

- Raw cards can use card API images or user-uploaded images.
- Graded cards should initially use the raw card image with a code-based slab/grade overlay.
- Do not permanently generate slab images for MVP unless a later ticket asks for it.
- Sealed products should be upload-first for MVP.
- If sealed product image is unavailable, show a placeholder.

## Testing and review rules

After changes, Codex should:

1. Run available tests or explain why none exist yet.
2. Run type/lint checks if configured.
3. Summarize changed files.
4. State what was intentionally not implemented.
5. Avoid broad refactors unrelated to the ticket.

## Git workflow

- Make one ticket per commit.
- Before each ticket, user should create or confirm a clean Git state.
- Do not mix backend, frontend, and large refactors unless the ticket requires it.
