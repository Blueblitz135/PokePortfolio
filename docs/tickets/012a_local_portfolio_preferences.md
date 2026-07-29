# Ticket 012A - Local Portfolio Preferences

## Goal

Make the `/settings` route a working portfolio-preferences page without
pretending that the single-user MVP has an authenticated account.

## Dependencies

- Ticket 009A: application shell and sidebar
- Ticket 010: asset detail page
- Ticket 011: manual pricing snapshots
- Ticket 012: currency layer

## Terminology

Call this page **Settings** or **Portfolio preferences**.

Do not call it an account profile. The MVP has no authentication, user model,
or server-side per-user settings.

## Requirements

- Replace the Settings placeholder with a readable settings page.
- Add a small preferences provider or hook.
- Use explicit Save and Reset actions.
- Store this versioned record under
  `pokemonPortfolio.preferences.v1`:

```json
{
  "version": 1,
  "displayCurrency": "CAD",
  "defaultAssetTypeFilter": "all"
}
```

- Validate every stored field against an allowlist.
- Handle unavailable storage and read/write exceptions without crashing.
- Default display currency to `CAD`.
- Use only currencies that ticket 012 actually supports.
- If real conversion is not implemented, keep CAD as the only enabled
  currency and explain why other currencies are unavailable.
- Never relabel a CAD amount with a USD, EUR, or other symbol without
  converting the numeric value.
- Keep conversion separate from formatting. Convert normalized CAD first, then
  format the converted amount with its actual currency code.
- If conversion fails, keep the CAD amount and CAD label. Never show the
  requested non-CAD symbol for an unconverted value.
- Route all existing monetary views, including the dashboard, asset detail,
  sealed-product detail, and purchase-lot displays, through the shared
  conversion-and-formatting pipeline.
- Allow the user to save and reset preferences.
- Use the saved `defaultAssetTypeFilter` when `/collection` is next entered or
  refreshed.
- Let temporary filter changes on the Collection page remain temporary; they
  must not silently overwrite the saved default.
- Safely fall back to defaults when stored JSON is missing, malformed, or from
  an unsupported future version.
- Explain that preferences are stored only in the current browser.

## Initial preference fields

Use exactly these initial fields:

- display currency, constrained by actual converter capability;
- default collection filter: `all`, `raw_card`, `graded_card`, or
  `sealed_product`.

Sidebar collapsed state may continue to be owned by the application shell.

## Acceptance criteria

- `/settings` displays the current preferences.
- Supported changes survive a page refresh.
- Reset restores CAD and other defaults.
- Invalid stored data does not crash the app.
- Unavailable `localStorage` does not crash the app.
- Unsupported currencies and unknown schema versions fall back to defaults.
- Missing or invalid default-filter values fall back to `all`.
- A saved default filter initializes the Collection page on its next entry or
  refresh.
- Every existing monetary view uses the shared conversion-and-formatting
  pipeline.
- A CAD numeric value can never render under a non-CAD code without
  conversion.
- Internal normalized market values remain CAD.
- Purchase-lot stored currency is not silently changed.
- No settings API, user table, or authentication is added.
- Frontend lint and production build pass.

Use an existing frontend test runner if one is already configured. Otherwise,
test pure preference parsing helpers if feasible without a broad tooling
change, and record a manual smoke checklist covering:

- valid save and refresh;
- reset;
- malformed JSON;
- unknown schema version;
- unavailable storage;
- unsupported currency;
- failed conversion retaining CAD amount and label.

## Not included

- name, email, avatar, password, or security editing;
- authentication;
- cloud synchronization;
- multi-device preferences;
- live or historical FX unless ticket 012 explicitly provides it;
- changing normalized stored amounts;
- pricing adapters;
- AI;
- alerts;
- scraping.

## Future real-profile boundary

If the application later needs a real profile, create a separate post-MVP
ticket after authentication exists. That ticket must cover:

- authenticated identity;
- a `User` model;
- protected profile endpoints;
- authorization;
- per-user asset ownership;
- migration from existing single-user data.

Do not simulate those features with browser-only fields.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/07_currency_strategy.md,
docs/12_frontend_navigation_and_search_plan.md,
docs/tickets/012_currency_layer.md, and
docs/tickets/012a_local_portfolio_preferences.md.

Implement ticket 012A only.

Build the local Portfolio preferences page at /settings. Persist only supported
display preferences in versioned localStorage and keep CAD as the default.
Never change only a currency symbol without converting the value.

Do not implement authentication, a User model, account/profile fields, cloud
sync, live FX, pricing adapters, AI, alerts, or scraping.
```
