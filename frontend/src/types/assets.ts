/** Shared API contracts for assets, metadata, lots, images, and price snapshots. */
import type { CurrencyCode } from "./currency";

/** Mutually exclusive portfolio categories used by backend pricing rules. */
export type AssetType = "raw_card" | "graded_card" | "sealed_product";

export type ExternalSource = "manual" | "tcgdex" | "pokemon_tcg_api";

export type RawCardCondition = "NM" | "LP" | "MP" | "DMG";

export type GradingCompany = "PSA" | "BGS" | "CGC" | "TAG" | "OTHER";

export type SealedProductType =
  | "booster_box"
  | "booster_pack"
  | "elite_trainer_box"
  | "booster_bundle"
  | "tin"
  | "collection_box"
  | "other";

/** Labels used to render the canonical sealed-product enum in forms. */
export const SEALED_PRODUCT_TYPE_OPTIONS: ReadonlyArray<{
  value: SealedProductType;
  label: string;
}> = [
  { value: "booster_box", label: "Booster box" },
  { value: "booster_pack", label: "Booster pack" },
  { value: "elite_trainer_box", label: "Elite Trainer Box" },
  { value: "booster_bundle", label: "Booster bundle" },
  { value: "tin", label: "Tin" },
  { value: "collection_box", label: "Collection box" },
  { value: "other", label: "Other" },
];

/** Provider or manual identity shared by raw and graded cards. */
export interface CardMetadata {
  id: number;
  external_source: ExternalSource;
  external_id: string | null;
  name: string;
  set_name: string;
  set_id: string | null;
  year: number | null;
  card_number: string;
  set_total: string | null;
  rarity: string | null;
  variant: string | null;
  image_url: string | null;
}

export interface RawCardDetails {
  condition: RawCardCondition;
}

export interface GradedCardDetails {
  grading_company: GradingCompany;
  grade: string;
  cert_number: string | null;
}

export interface SealedProductMetadata {
  id: number;
  product_name: string;
  set_name: string | null;
  year: number | null;
  sealed_product_type: SealedProductType;
  is_pokemon_center_exclusive: boolean | null;
  external_source: string | null;
  external_id: string | null;
  image_url: string | null;
}

/** One dated acquisition; asset quantity is derived from all of its lots. */
export interface PurchaseLot {
  id: number;
  asset_id: number;
  purchase_date: string;
  quantity: number;
  purchase_price_per_unit: string;
  currency: CurrencyCode;
  created_at: string;
  updated_at: string;
}

export interface AssetImage {
  id: number;
  asset_id: number;
  image_type: "uploaded" | "api" | "generated_overlay" | "placeholder";
  url_or_path: string;
  is_primary: boolean;
  created_at: string;
}

/** One normalized per-unit market observation for an asset. */
export interface PriceSnapshot {
  id: number;
  asset_id: number;
  market_price_per_unit: string;
  currency: CurrencyCode;
  source: "manual";
  confidence: string | null;
  observed_at: string;
}

/** Backend-calculated holdings and unrealized performance for one asset. */
export interface AssetSummary {
  currency: CurrencyCode;
  total_quantity: number;
  total_cost: string;
  average_cost_per_unit: string | null;
  market_price_per_unit: string | null;
  total_market_value: string | null;
  profit_loss: string | null;
  roi_percent: string | null;
}

/** Fully hydrated asset returned by collection and detail endpoints. */
export interface AssetResponse {
  market_pricing?: MarketPricing | null;
  id: number;
  asset_type: AssetType;
  display_name: string;
  user_note: string | null;
  created_at: string;
  updated_at: string;
  images: AssetImage[];
  primary_image_url: string;
  purchase_lots: PurchaseLot[];
  latest_price_snapshot: PriceSnapshot | null;
  summary: AssetSummary;
  card_metadata: CardMetadata | null;
  raw_details: RawCardDetails | null;
  graded_details: GradedCardDetails | null;
  sealed_product_metadata: SealedProductMetadata | null;
}

export interface MarketPricing {
  state: string;
  detail: string;
  source: string;
  source_url: string;
  fetched_at: string;
  observed_at: string | null;
  history_duration: string;
  growth_percent: string | null;
  tcgplayer?: {
    state: string;
    note: string;
    observed_at: string | null;
    variants: Array<{
      printing: string;
      market_price_cad: string | null;
      low_price_cad: string | null;
      median_price_cad: string | null;
      high_price_cad: string | null;
    }>;
  } | null;
}

export type SealedProductAsset = AssetResponse & {
  asset_type: "sealed_product";
  sealed_product_metadata: SealedProductMetadata;
};

/** Payload for a new sealed asset and its required product metadata. */
export interface SealedProductCreatePayload {
  asset_type: "sealed_product";
  display_name: string;
  user_note: string | null;
  sealed_product_metadata: {
    product_name: string;
    set_name: string | null;
    year: number | null;
    sealed_product_type: SealedProductType;
    is_pokemon_center_exclusive: boolean;
  };
}

/** Structured card identity used when creating raw or graded assets. */
export interface CardMetadataCreatePayload {
  external_source: ExternalSource;
  external_id: string;
  name: string;
  set_name: string;
  set_id: string;
  year: number | null;
  card_number: string;
  set_total: string | null;
  rarity: string | null;
  variant: null;
  image_url: string | null;
}

interface CardAssetCreateBase {
  display_name: string;
  user_note: string | null;
  card_metadata: CardMetadataCreatePayload;
}

export interface RawCardCreatePayload extends CardAssetCreateBase {
  asset_type: "raw_card";
  raw_details: {
    condition: RawCardCondition;
  };
}

export interface GradedCardCreatePayload extends CardAssetCreateBase {
  asset_type: "graded_card";
  graded_details: {
    grading_company: GradingCompany;
    grade: string;
    cert_number: string | null;
  };
}

export type CardAssetCreatePayload =
  | RawCardCreatePayload
  | GradedCardCreatePayload;

export type AssetCreatePayload =
  | CardAssetCreatePayload
  | SealedProductCreatePayload;

/** Payload for recording a new acquisition under an existing asset. */
export interface PurchaseLotCreatePayload {
  purchase_date: string;
  quantity: number;
  purchase_price_per_unit: string;
  currency: CurrencyCode;
}

export interface PurchaseLotUpdatePayload {
  purchase_date?: string;
  quantity?: number;
  purchase_price_per_unit?: string;
  currency?: CurrencyCode;
}

/** User-entered normalized market value saved as a manual snapshot. */
export interface ManualPriceSnapshotCreatePayload {
  market_price_per_unit: string;
  currency: CurrencyCode;
  source: "manual";
  confidence: 0.5;
}

/** Narrow an API asset to one with guaranteed sealed-product metadata. */
export function isSealedProductAsset(
  asset: AssetResponse,
): asset is SealedProductAsset {
  return (
    asset.asset_type === "sealed_product" &&
    asset.sealed_product_metadata !== null
  );
}

/** Convert a sealed-product enum value to its user-facing label. */
export function getSealedProductTypeLabel(type: SealedProductType): string {
  return (
    SEALED_PRODUCT_TYPE_OPTIONS.find((option) => option.value === type)?.label ??
    type
  );
}

/** Convert an asset category to its user-facing singular label. */
export function getAssetTypeLabel(type: AssetType): string {
  const labels: Record<AssetType, string> = {
    raw_card: "Raw card",
    graded_card: "Graded card",
    sealed_product: "Sealed product",
  };

  return labels[type];
}
