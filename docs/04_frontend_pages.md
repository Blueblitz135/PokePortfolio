# 04 - Frontend Pages

## Page list

### Collection dashboard

Route:

```txt
/collection
```

Purpose:

Show all assets the user owns.

Fields to display:

- image
- display name
- asset type
- total quantity
- average cost
- market price per unit if available
- total market value if available
- profit/loss if available
- ROI if available

Actions:

- add asset
- click asset to view details
- filter by raw cards, graded cards, sealed products
- choose display currency later

---

### Add asset page/modal

Route:

```txt
/assets/new
```

Purpose:

Allow user to create a raw card, graded card, or sealed product.

Flow:

1. User selects asset type.
2. User enters metadata manually or searches card metadata.
3. User optionally uploads image.
4. User adds first purchase lot.
5. Asset appears in collection.

---

### Asset detail page

Route:

```txt
/assets/:assetId
```

Sections:

1. Header
   - image
   - display name
   - asset type
   - note

2. Metadata
   - card metadata for cards
   - sealed product metadata for sealed products
   - grade details for graded cards
   - condition details for raw cards

3. Purchase lots
   - table of every purchase record
   - edit lot
   - delete lot
   - add lot

4. Summary
   - total quantity
   - total cost
   - average cost
   - market price per unit
   - total market value
   - profit/loss
   - ROI

5. Images
   - primary image
   - upload/change image

---

### Card search page or component

Used inside Add Asset.

Features:

- search input
- display card image
- display set name
- display card number/set total
- select card

---

## Graded card image UI

For graded cards, use the raw/API card image as the visual base, then add a code-based overlay.

Example UI:

```txt
+-----------------------+
| PSA 10                |
| GEM MINT              |
|                       |
|      Card Image       |
|                       |
+-----------------------+
```

This should be HTML/CSS at first, not a generated image file.

## Empty states

Collection empty state:

```txt
No assets yet. Add your first card or sealed product.
```

Price unavailable state:

```txt
Market price not available yet.
```

Image unavailable state:

```txt
Use placeholder image.
```
