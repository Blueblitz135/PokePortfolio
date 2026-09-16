import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { PortfolioPreferencesProvider } from "../preferences/PortfolioPreferencesProvider";
import type { AssetResponse } from "../types/assets";
import { CollectionAssetCard } from "./CollectionAssetCard";
import { MarketPriceEvidence } from "./MarketPriceEvidence";

afterEach(cleanup);

const asset = {
  id: 1, asset_type: "raw_card", display_name: "Umbreon VMAX",
  card_metadata: { name: "Umbreon VMAX", set_name: "Evolving Skies", card_number: "215", set_total: "203" },
  raw_details: { condition: "NM" }, primary_image_url: "/card.webp",
  summary: { currency: "CAD", total_quantity: 2, total_cost: "200", average_cost_per_unit: "100", market_price_per_unit: "150", total_market_value: "300", profit_loss: "100", roi_percent: "50" },
  market_pricing: { state: "available", detail: "Latest available market estimate.", source: "Marketplace and verified store sales", source_url: "https://justtcg.com/features", observed_at: "2026-09-15T12:00:00Z", fetched_at: "2026-09-15T13:00:00Z", history_duration: "90d", growth_percent: null,
    tcgplayer: { state: "available", note: "Raw-card marketplace reference.", observed_at: "2026-09-15T12:00:00Z", variants: [{ printing: "holofoil", market_price_cad: "140", low_price_cad: "120", median_price_cad: "145", high_price_cad: "180" }] } },
} as AssetResponse;

it("shows refreshed market price, holdings value, profit and ROI with attribution", () => {
  render(<PortfolioPreferencesProvider><CollectionAssetCard asset={asset} showDetailsLink={false} /></PortfolioPreferencesProvider>);
  for (const [label, amount] of [["Latest market price", "150.00"], ["Total market value", "300.00"], ["Profit / loss", "100.00"], ["ROI", "50%"]]) {
    expect(screen.getByText(label).nextElementSibling?.textContent).toContain(amount);
  }
  expect(screen.getByRole("link", { name: "Marketplace and verified store sales" })).toBeTruthy();
});

it("shows TCGPlayer market, low, median and high separately", () => {
  render(<PortfolioPreferencesProvider><MarketPriceEvidence asset={asset} detailed /></PortfolioPreferencesProvider>);
  for (const [label, amount] of [["Market", "140.00"], ["Low", "120.00"], ["Median", "145.00"], ["High", "180.00"]]) {
    expect(screen.getByText(label).nextElementSibling?.textContent).toContain(amount);
  }
});

it("makes unavailable prices explicit without implying a successful refresh", () => {
  const unavailable = { ...asset, market_pricing: { ...asset.market_pricing!, state: "unmatched", detail: "No unique price match; saved prices are shown.", tcgplayer: null } };
  render(<PortfolioPreferencesProvider><MarketPriceEvidence asset={unavailable} /></PortfolioPreferencesProvider>);
  expect(screen.getByRole("status").textContent).toContain("saved prices");
  expect(screen.queryByText(/Price observed/)).toBeNull();
});
