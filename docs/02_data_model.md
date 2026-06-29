# 02 - Data Model

## Main entities

### Asset

Represents one tracked market asset.

Examples:

- Umbreon VMAX raw NM
- Umbreon VMAX PSA 10
- Evolving Skies Booster Box sealed

Suggested fields:

```txt
id
asset_type: raw_card | graded_card | sealed_product
display_name
user_note
created_at
updated_at
```

Important: `Asset` does not directly store quantity. Quantity comes from `PurchaseLot`.

---

### CardMetadata

Used for both raw and graded cards.

Suggested fields:

```txt
id
asset_id
external_source: tcgdex | pokemon_tcg_api | manual
external_id
name
set_name
set_id
year
card_number
set_total
rarity
variant
image_url
```

Example:

```txt
name = Umbreon VMAX
set_name = Evolving Skies
card_number = 215
set_total = 203
```

Do not store `215/203` only as part of the card title. Store it as structured metadata.

---

### RawCardDetails

Can be separate table or fields attached to card metadata depending on implementation.

```txt
asset_id
condition: NM | LP | MP | DMG
```

Raw condition is part of the owned asset identity.

---

### GradedCardDetails

```txt
asset_id
grading_company: PSA | BGS | CGC | TAG | OTHER
grade
cert_number optional
```

Graded card pricing must not be mixed with raw card pricing.

---

### SealedProductMetadata

Suggested fields:

```txt
id
asset_id
product_name
set_name
year
sealed_product_type: booster_box | booster_pack | elite_trainer_box | booster_bundle | tin | collection_box | other
is_pokemon_center_exclusive optional
external_source optional
external_id optional
image_url optional
```

MVP rules:

- Do not track booster pack art.
- Do not track ETB artwork version.
- Do not track tin artwork version.
- Booster bundle always means 6 packs, so it does not need `pack_count`.

---

### PurchaseLot

Represents one time the user bought a quantity of an asset.

Suggested fields:

```txt
id
asset_id
purchase_date
quantity
purchase_price_per_unit
currency = CAD
created_at
updated_at
```

Example:

```txt
asset = Evolving Skies Booster Box
purchase_date = 2025-08-01
quantity = 1
purchase_price_per_unit = 750 CAD
```

Later, the user can add another lot:

```txt
purchase_date = 2026-02-15
quantity = 2
purchase_price_per_unit = 900 CAD
```

The asset detail page summarizes both lots.

---

### AssetImage

```txt
id
asset_id
image_type: uploaded | api | generated_overlay | placeholder
url_or_path
is_primary
created_at
```

For MVP, local file storage is acceptable. Later, use S3, Cloudinary, Supabase Storage, or another object store.

---

### PriceSnapshot

Represents the market price estimate at a point in time.

```txt
id
asset_id
market_price_per_unit
currency = CAD
source: manual | tcgdex | pokemon_tcg_api | justtcg | ebay | blended
confidence
observed_at
metadata_json
```

For MVP, allow manual price snapshots. Later, external adapters can create these automatically.

---

## Derived calculations

```txt
total_quantity = sum(purchase_lot.quantity)
total_cost = sum(purchase_lot.quantity * purchase_lot.purchase_price_per_unit)
average_cost = total_cost / total_quantity
market_value = latest_market_price_per_unit * total_quantity
profit_loss = market_value - total_cost
roi_percent = profit_loss / total_cost * 100
```

If market price is missing, market-dependent fields should return `null`.
