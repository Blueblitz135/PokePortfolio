# Ticket 005 - Asset Image Uploads

## Goal

Allow every asset to have an uploaded image.

## Requirements

- Upload image for any asset.
- Save image locally for development.
- Store image path/metadata in database.
- Mark one image as primary.
- Return image URL/path in asset responses.
- Use placeholder if no image exists.

## Accepted file types

- jpg
- jpeg
- png
- webp

## Acceptance criteria

- User can upload image for raw card.
- User can upload image for graded card.
- User can upload image for sealed product.
- Asset list/detail returns primary image.
- Invalid file type is rejected.

## Codex prompt

```txt
Read AGENTS.md, CODING_RULES.md, docs/06_image_strategy.md, and docs/tickets/005_asset_image_uploads.md.
Implement image upload support.
Keep storage local for MVP.
Do not implement external image APIs yet.
```
