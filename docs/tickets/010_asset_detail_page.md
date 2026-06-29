# Ticket 010 - Asset Detail Page

## Goal

Build the asset detail page.

## Page

```txt
/assets/:assetId
```

## Sections

- image/header
- metadata
- note
- purchase lots table
- add purchase lot form
- edit/delete purchase lot
- summary calculations
- market price snapshot if available

## Acceptance criteria

- User can view one asset.
- User can add purchase lot from detail page.
- User can edit purchase lot.
- User can delete purchase lot.
- Summary updates after lot changes.
- UI handles missing image and missing market price.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/04_frontend_pages.md, docs/03_api_contract.md, and docs/tickets/010_asset_detail_page.md.
Implement the asset detail page and purchase lot UI.
```
