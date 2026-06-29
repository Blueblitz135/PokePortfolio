# 00 - Project Overview

## Product vision

Build a Pokémon portfolio investment app that lets users track raw cards, graded cards, and sealed products like investment assets.

The app should answer:

- What do I own?
- How much did I pay?
- How many copies/units do I own?
- What is the current estimated market value?
- Am I up or down?
- Which assets have the best or worst performance?

## Supported asset categories

### Raw cards

Examples:

- Umbreon VMAX Evolving Skies raw NM
- Charizard Base Set raw LP
- Pikachu promo raw MP

Raw cards require condition tracking.

Supported raw conditions for MVP:

```txt
NM = Near Mint
LP = Lightly Played
MP = Moderately Played
DMG = Damaged
```

### Graded cards

Examples:

- Umbreon VMAX PSA 10
- Charizard Base Set PSA 9
- Lugia V BGS 9.5

Graded cards require grading company and numeric grade tracking.

Supported grading companies for MVP:

```txt
PSA
BGS
CGC
TAG
OTHER
```

### Sealed products

Examples:

- Evolving Skies Booster Box
- Crown Zenith Elite Trainer Box
- 151 Booster Bundle
- Pokémon Center Elite Trainer Box
- Booster pack
- Tin
- Collection box

Sealed products require sealed product type, set/product name, and purchase records. Pack art is not tracked in MVP.

## Core idea

The app should work like a simple collectible investment tracker first, then grow into a market intelligence platform later.

The correct build order is:

1. Manual portfolio tracker
2. Images and asset detail pages
3. External card metadata search
4. Basic pricing snapshots
5. Better pricing adapters
6. AI analysis
7. Alerts and advanced analytics
