# Ticket 010A - Search Cards and Add to Collection

## Goal

Build the frontend workflow that lets a user search for a Pokemon card through
the existing TCGdex-backed endpoint, confirm the result, and add an owned raw
or graded copy to the collection.

Selecting a result must not create an asset. Creation requires explicit user
confirmation.

## Dependencies

- Ticket 003: asset CRUD
- Ticket 004: purchase lots
- Ticket 005: card image behavior
- Ticket 006: card metadata search
- Ticket 007: graded-card display
- Ticket 009: collection dashboard
- Ticket 009A: application shell and sidebar
- Ticket 010: asset detail page

## Route

```txt
/search
```

The sidebar Search item should navigate to this page.

## Existing endpoints

```http
GET /api/search/cards?q={query}
POST /api/assets
POST /api/assets/{assetId}/purchase-lots
```

Use the existing endpoints. Do not create a second card-search endpoint unless
the existing contract is genuinely insufficient.

## Search result fields

Each normalized result contains:

- `external_source`
- `external_id`
- `name`
- `set_name`
- `set_id`
- `year`
- `card_number`
- `set_total`
- `rarity`
- `image_url`

These fields describe card identity. Display them for confirmation instead of
asking the user to enter them again.

## User flow

1. The user submits a trimmed search query between 1 and 100 characters.
2. Display loading, error, no-results, and results states.
3. Each result displays:
   - card image or placeholder;
   - name;
   - set;
   - structured card number such as `215/203`;
   - rarity and year when present.
4. The user selects one result.
5. The user chooses raw or graded.
6. Collect ownership-specific fields.
7. Collect the first purchase lot.
8. Display a final confirmation.
9. Create the asset only after confirmation.
10. Create the required purchase lot using the returned asset ID.
11. Offer to open `/assets/:assetId` or return to `/collection`.

## Ownership fields

### Raw card

Required:

- condition: `NM`, `LP`, `MP`, or `DMG`

Optional:

- overall user note

### Graded card

Required:

- grading company: `PSA`, `BGS`, `CGC`, `TAG`, or `OTHER`
- grade greater than 0 and no greater than 10

Optional:

- certification number
- overall user note

Certification number is limited to 100 characters.

### First purchase lot

Require:

- purchase date;
- quantity as a positive integer;
- purchase price per unit of zero or greater, with at most 12 total digits and
  no more than two decimal places.

Send currency as uppercase `CAD`.

Quantity must never be added to the asset payload.

## Asset payload rules

- Set `display_name` to the selected result's `name`. The search contract
  already limits it to 255 characters.
- Do not put `card_number` or `set_total` in `display_name`.
- Copy all normalized search identity fields into `card_metadata`.
- For raw cards, send `raw_details` and omit `graded_details`.
- For graded cards, send `graded_details` and omit `raw_details`.
- Preserve the search result's `image_url`.
- Set `variant` to `null`. The current search contract does not return a
  printing variant, so do not infer holo or reverse-holo information.
- The asset response should use the card metadata image as a fallback when no
  uploaded primary image exists. Make the smallest backend adjustment needed
  if the existing response still returns only the generic placeholder.

This ticket may include that focused backend service change and backend tests.
The fallback priority should be:

1. uploaded primary image;
2. `card_metadata.image_url`;
3. generic placeholder.

Do not create an `AssetImage` record for the provider URL.

## Save and error behavior

- Disable confirmation while saving to prevent double submission.
- Never automatically retry `POST /api/assets`.
- Create the asset first.
- Create the purchase lot only after receiving the new asset ID.
- If asset creation fails, remain on the confirmation step.
- Treat a validation or other definite 4xx response as a failed creation that
  the user can correct before trying again.
- If asset creation succeeds but the lot fails:
  - do not create the asset again;
  - retain the asset ID;
  - report the partial success clearly;
  - allow retrying only the lot request;
  - offer links to the asset and collection.
- If a network timeout or server error makes asset creation ambiguous, explain
  that the result could not be confirmed and ask the user to check Collection
  before submitting again.
- Cancel an older search request or ignore its response when a newer query is
  submitted.
- Clear the selected result when a genuinely new search begins.

## Sealed-product limitation

TCGdex searches cards, not a reliable sealed-product catalog.

Therefore:

- search results can be added only as raw or graded cards;
- do not show sealed product as a choice for a TCGdex card result;
- keep the existing manual/upload-first sealed workflow accessible;
- explain briefly that sealed-product search is unavailable;
- do not call the card endpoint for sealed products.

A real sealed search requires a separate provider and ticket.

## Suggested components

```txt
SearchPage
CardSearchForm
CardSearchResults
CardSearchResultCard
AddSearchedCardForm
CardAddConfirmation
```

Also add:

- a typed frontend card-search API function;
- generic typed asset-creation support;
- pure payload-building helpers where useful.

## Acceptance criteria

- Search submits a trimmed, safely encoded query.
- Search rejects trimmed queries outside the 1-to-100-character contract.
- Loading, error, retry, no-results, and results states are clear.
- Results render normalized metadata and an image fallback.
- Selecting a result does not create an asset.
- Explicit confirmation is required.
- Raw payloads contain only raw details.
- Graded payloads contain only graded details.
- Card number and set total remain separate structured fields.
- Display name does not contain the card number.
- Grade validation allows more than 0 and at most 10, with at most one decimal
  place.
- The required purchase lot uses uppercase CAD and the returned asset ID.
- Retrying a failed lot does not create a duplicate asset.
- A successful flow can open the asset detail page or collection.
- Sealed products are clearly outside this search flow.
- No pricing data is requested or displayed.
- Search controls are labelled and results can be selected by keyboard.
- Loading and error status are announced appropriately.
- Existing collection and sealed-product workflows still function.

## Tests and checks

The project does not yet have a frontend test runner. Do not add a broad test
infrastructure change before ticket 013. Record and run a manual smoke
checklist that covers:

- trimmed and encoded queries;
- loading, empty, error, and success states;
- selection without creation;
- raw and graded payload construction;
- card number excluded from display name;
- asset POST followed by lot POST;
- asset failure;
- definite 4xx failure versus ambiguous network or 5xx failure;
- partial lot failure;
- lot retry without a second asset POST;
- double-submission prevention;
- stale search-response prevention;
- missing and broken images.

```powershell
npm run lint
npm run build
```

Add focused backend tests for any card-image fallback service change, then run
the complete backend regression suite.

## Not included

- sealed-product search;
- pricing;
- automatic asset creation;
- duplicate detection or automatic merging;
- downloading or caching provider images;
- image uploads;
- authentication or profile settings;
- AI;
- alerts;
- scraping.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/03_api_contract.md,
docs/04_frontend_pages.md, docs/08_external_api_decision.md,
docs/12_frontend_navigation_and_search_plan.md, and
docs/tickets/010a_card_search_add_to_collection.md.

Implement ticket 010A only.

Build the frontend card-search and confirmation workflow using the existing
TCGdex-backed endpoint. Let the user add the selected card as raw or graded and
create its first purchase lot.

Do not implement sealed-product search, pricing, authentication, profile
settings, AI, alerts, scraping, or automatic duplicate merging.
```
