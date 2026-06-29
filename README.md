# Pokémon Portfolio Investment App - Codex Build Pack

This folder contains the markdown files you should place in your project repository before asking Codex to build the app.

The goal is to turn the full product specification into small, testable implementation tickets. Do not ask Codex to build the entire app in one prompt. Instead, give Codex one ticket at a time, review the diff, run the app, then commit.

## Recommended repo structure after setup

```txt
pokemon-portfolio/
  AGENTS.md
  CODING_RULES.md
  README.md
  docs/
    00_project_overview.md
    01_mvp_scope.md
    02_data_model.md
    03_api_contract.md
    04_frontend_pages.md
    05_pricing_engine.md
    06_image_strategy.md
    07_currency_strategy.md
    08_external_api_decision.md
    09_multiagent_workflow.md
    10_step_by_step_build_guide.md
    11_risks_and_concerns.md
    tickets/
      001_project_setup.md
      002_database_models.md
      003_manual_collection_crud.md
      004_purchase_lots_and_calculations.md
      005_asset_image_uploads.md
      006_card_metadata_search.md
      007_graded_card_overlay.md
      008_sealed_product_support.md
      009_frontend_collection_dashboard.md
      010_asset_detail_page.md
      011_pricing_engine_placeholder.md
      012_currency_layer.md
      013_tests_and_quality.md
      014_external_pricing_adapters.md
```

## Build rule

Work in this order:

1. Manual collection app
2. Purchase lots and calculations
3. Image upload system
4. Card metadata search
5. Graded card overlay
6. Sealed product support
7. Currency system
8. Pricing engine placeholder
9. Real external pricing adapters
10. AI assistant later

## First Codex prompt

Paste this into the VS Code Codex agent after copying these files into your repo:

```txt
Read AGENTS.md, CODING_RULES.md, docs/00_project_overview.md, docs/01_mvp_scope.md, and docs/tickets/001_project_setup.md.

Implement ticket 001 only.

Do not implement external APIs, pricing, AI, auth, alerts, or scraping.

After coding:
- list changed files
- explain how to run backend and frontend
- run the checks that are available
- tell me what to commit
```
