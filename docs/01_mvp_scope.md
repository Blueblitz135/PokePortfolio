# 01 - MVP Scope

## MVP objective

Build a working app where a user can manually add Pokémon assets, add purchase records, upload/view images, and see basic portfolio calculations.

## MVP must include

### Backend

- FastAPI app
- Database models
- CRUD endpoints for assets
- CRUD endpoints for purchase lots
- Asset calculation service
- Image upload endpoint
- Simple price snapshot model
- CAD as default currency

### Frontend

- Collection dashboard
- Add asset form
- Asset detail page
- Purchase lot table
- Add/edit/delete purchase lot UI
- Image display and upload UI
- Basic portfolio summary

### Asset support

- Raw cards
- Graded cards
- Sealed products

### Calculation support

For each asset:

- total quantity
- total cost
- average cost per unit
- latest market price per unit, if available
- total market value, if market price exists
- profit/loss, if market price exists
- ROI percentage, if market price exists

## MVP should not include yet

- AI assistant
- real eBay ingestion
- scraping
- alerts
- auto bidding
- user authentication
- taxes/fees/shipping/source tracking
- advanced charts
- pack art-specific valuation
- graded card certification lookup

## Why pricing comes later

The app needs a correct internal data model before pricing matters. If purchase lots, asset identity, and images are wrong, external pricing will become messy.

Build manual market price snapshots first. Then replace them with real API adapters later.
