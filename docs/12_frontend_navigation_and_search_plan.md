# 12 - Frontend Navigation, Search, and Settings Plan

## Decision

Do not add the sidebar, search-to-collection workflow, and settings page to
ticket 009.

Ticket 009 is the collection dashboard and is already a coherent staged
change. Mixing the redesign into it would combine page layout, routing,
external search state, asset creation, purchase-lot creation, and settings
persistence in one commit.

Commit ticket 009 first, then add the new work as small tickets at the points
where their dependencies are ready.

## Recommended order

```txt
009   Collection dashboard
009A  Application shell and collapsible sidebar
010   Asset detail page
010A  Card search and add-to-collection workflow
011   Manual pricing snapshots
012   Currency layer
012A  Local application preferences
013   Tests and quality
014   External pricing adapter
015+  Authentication and real user profiles, if wanted
```

### Why this order

- Build the application shell before ticket 010 so every later page uses the
  same routing and navigation structure.
- Build search-to-add after ticket 010 so a newly created asset has a working
  detail page and purchase-lot recovery flow.
- Build settings after ticket 012 so a display-currency preference cannot show
  a different currency symbol without converting the amount.
- Defer real user profiles until authentication and per-user ownership are
  explicitly added after the MVP.

## Target navigation

The application shell should provide these primary routes:

| Sidebar item | Route | Purpose |
| --- | --- | --- |
| Collection | `/collection` | View and filter owned assets |
| Search | `/search` | Find cards and add them to the collection |
| Settings | `/settings` | Edit local portfolio/display preferences |

Related routes:

| Route | Purpose |
| --- | --- |
| `/assets/:assetId` | View and edit one asset |
| `/sealed-products` | Preserve the upload-first sealed-product workflow |

The sidebar should collapse to an icon rail on desktop and become an
off-canvas drawer on small screens.

## Search-to-collection flow

Ticket 006 already provides:

```http
GET /api/search/cards?q={query}
```

The future frontend flow should:

1. Let the user submit a card query.
2. Display loading, error, no-results, and results states.
3. Show each card's image, name, set, structured card number, rarity, and year.
4. Let the user select a result without creating anything yet.
5. Ask whether the owned copy is raw or graded.
6. Ask only for ownership-specific details:
   - raw condition, or
   - grading company, grade, and optional certification number.
7. Collect the first purchase lot so the new asset represents an owned item.
8. Show a final confirmation.
9. Create the asset with `POST /api/assets`.
10. Create the required lot with
    `POST /api/assets/{assetId}/purchase-lots`.
11. Navigate to the new asset detail page or back to the collection.

Selecting a result must never create an asset automatically.

### Metadata mapping

Copy normalized provider data into `card_metadata`:

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

Keep `card_number` and `set_total` as separate fields. Do not add the card
number to `display_name`.

Quantity belongs only to the purchase lot.

### Partial-save behavior

Asset creation and purchase-lot creation use two existing requests.

If the asset is created but the lot fails:

- do not create the asset again;
- retain the new asset ID;
- explain that the card was added but the purchase record failed;
- allow retrying only the purchase-lot request;
- provide links to the asset and collection.

## Sealed-product limitation

TCGdex is a card catalog. It is not a reliable sealed-product catalog.

The first search workflow therefore supports:

- raw cards;
- graded cards.

It does not support sealed-product search. Keep the current manual,
upload-first sealed workflow until a sealed metadata provider and normalized
backend contract are chosen in a separate ticket.

## Settings versus profile

The MVP has no authentication, user table, or per-user authorization.

For the MVP, the sidebar tab should be called **Settings** or
**Portfolio preferences**, not an account profile. It may store browser-local
preferences such as:

- supported display currency;
- sidebar collapsed state;
- other presentation-only defaults added deliberately later.

Do not add local-only email, password, avatar, or security fields. Those would
look like an account without providing real authentication or persistence.

A real profile requires a post-MVP ticket covering:

- authentication;
- a `User` model;
- per-user asset ownership;
- protected profile endpoints;
- authorization tests;
- migration of existing single-user data.

## Currency correctness

CAD remains the normalized MVP currency.

Ticket 012 may provide only a currency interface or placeholder. Ticket 012A
should consume that capability contract, but it must remain CAD-only unless a
real supported conversion path exists.

The settings page must never change only the currency symbol. A USD or EUR
display option can be enabled only when the application can convert the
numeric value. Until then, CAD should be the only enabled display currency.

## Features intentionally deferred

- real account/profile editing;
- authentication;
- sealed-product search;
- automatic duplicate matching or asset merging;
- pricing inside metadata search;
- image downloading or caching;
- AI recommendations;
- alerts;
- scraping.
