# 06 - Image Strategy

## Goal

Every asset should have an image in collection view and asset detail view.

## Raw cards

Preferred image source order:

1. User-uploaded image
2. TCGdex card image
3. Pokémon TCG API card image
4. Placeholder

Raw cards are easiest because card APIs usually provide clean card images.

## Graded cards

Use the same base card image as the raw card, then apply a code-based slab/grade overlay.

Do not require the user to upload a real slab photo in MVP.

### MVP graded image approach

Frontend renders:

- base card image
- slab-like container border
- label area above card
- grading company
- grade

Example:

```txt
PSA 10
Umbreon VMAX
215/203
[card image]
```

### Why code-based overlay is best for MVP

- No image generation pipeline needed.
- Easy to change design.
- Works for PSA/BGS/CGC/TAG.
- Avoids needing real cert images.
- Can be exported to a permanent image later if needed.

### Future improvement

Later, generate a permanent composited image server-side using Pillow or frontend canvas.

## Sealed products

Sealed products are the hardest image category.

Preferred image source order:

1. User-uploaded image
2. Manually curated local image uploaded by the user/admin
3. External product image if a reliable product API is added later
4. Placeholder by sealed product type

### MVP rule

Use upload-first sealed product images.

This is reliable because external free APIs may not consistently provide sealed product images for booster boxes, ETBs, tins, collection boxes, and older products.

### Placeholder examples

Use generic placeholders like:

- Booster Box Placeholder
- Booster Pack Placeholder
- Elite Trainer Box Placeholder
- Booster Bundle Placeholder
- Tin Placeholder
- Collection Box Placeholder

## File storage

MVP:

- Save uploaded images locally in `backend/uploads/`.
- Store image path in the database.

Later:

- Use S3, Supabase Storage, Cloudinary, or similar object storage.

## Accepted file types

For MVP:

```txt
jpg
jpeg
png
webp
```

Set a reasonable file size limit, such as 5 MB.
