# 03 - API Contract

This document defines the API shape Codex should build toward.

Base path:

```txt
/api
```

## Assets

### Create asset

```http
POST /api/assets
```

Example request for raw card:

```json
{
  "asset_type": "raw_card",
  "display_name": "Umbreon VMAX - Evolving Skies - Raw NM",
  "user_note": "Long-term hold",
  "card_metadata": {
    "name": "Umbreon VMAX",
    "set_name": "Evolving Skies",
    "year": 2021,
    "card_number": "215",
    "set_total": "203",
    "rarity": "Secret Rare",
    "image_url": "https://example.com/image.png"
  },
  "raw_details": {
    "condition": "NM"
  }
}
```

Example request for graded card:

```json
{
  "asset_type": "graded_card",
  "display_name": "Umbreon VMAX - Evolving Skies - PSA 10",
  "card_metadata": {
    "name": "Umbreon VMAX",
    "set_name": "Evolving Skies",
    "year": 2021,
    "card_number": "215",
    "set_total": "203"
  },
  "graded_details": {
    "grading_company": "PSA",
    "grade": "10"
  }
}
```

Example request for sealed product:

```json
{
  "asset_type": "sealed_product",
  "display_name": "Evolving Skies Booster Box",
  "sealed_product_metadata": {
    "product_name": "Evolving Skies Booster Box",
    "set_name": "Evolving Skies",
    "year": 2021,
    "sealed_product_type": "booster_box"
  }
}
```

### List assets

```http
GET /api/assets
```

Response should include summary calculations.

### Get one asset

```http
GET /api/assets/{asset_id}
```

Response should include:

- asset metadata
- card or sealed metadata
- purchase lots
- images
- latest price snapshot
- calculated summary

### Update asset

```http
PATCH /api/assets/{asset_id}
```

### Delete asset

```http
DELETE /api/assets/{asset_id}
```

---

## Purchase lots

### Add purchase lot

```http
POST /api/assets/{asset_id}/purchase-lots
```

```json
{
  "purchase_date": "2026-06-27",
  "quantity": 2,
  "purchase_price_per_unit": 750.00,
  "currency": "CAD"
}
```

### Update purchase lot

```http
PATCH /api/purchase-lots/{lot_id}
```

### Delete purchase lot

```http
DELETE /api/purchase-lots/{lot_id}
```

---

## Images

### Upload image

```http
POST /api/assets/{asset_id}/images
Content-Type: multipart/form-data
```

Fields:

```txt
file
is_primary optional
```

### List images for asset

```http
GET /api/assets/{asset_id}/images
```

---

## Price snapshots

### Add manual price snapshot

```http
POST /api/assets/{asset_id}/price-snapshots
```

```json
{
  "market_price_per_unit": 1200.00,
  "currency": "CAD",
  "source": "manual",
  "confidence": 0.5
}
```

---

## Search

### Card metadata search

```http
GET /api/search/cards?q=umbreon vmax evolving skies
```

Returns normalized card metadata from TCGdex first, then Pokémon TCG API fallback later.

### Sealed product search

```http
GET /api/search/sealed?q=evolving skies booster box
```

MVP can return local/manual placeholder results. Real sealed search can be implemented later.

---

## Currency

### Supported currencies

```http
GET /api/currencies
```

### Convert amount

```http
GET /api/currency/convert?amount=100&from=USD&to=CAD
```

Use this later when external pricing returns USD/EUR/etc.
