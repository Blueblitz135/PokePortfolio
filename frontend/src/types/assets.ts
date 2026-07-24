export type AssetType = "raw_card" | "graded_card" | "sealed_product";

export type SealedProductType =
  | "booster_box"
  | "booster_pack"
  | "elite_trainer_box"
  | "booster_bundle"
  | "tin"
  | "collection_box"
  | "other";

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

export interface PurchaseLot {
  id: number;
  asset_id: number;
  purchase_date: string;
  quantity: number;
  purchase_price_per_unit: string;
  currency: string;
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

export interface AssetSummary {
  total_quantity: number;
  total_cost: string;
  average_cost_per_unit: string | null;
  market_price_per_unit: string | null;
  total_market_value: string | null;
  profit_loss: string | null;
  roi_percent: string | null;
}

export interface AssetResponse {
  id: number;
  asset_type: AssetType;
  display_name: string;
  user_note: string | null;
  created_at: string;
  updated_at: string;
  images: AssetImage[];
  primary_image_url: string;
  purchase_lots: PurchaseLot[];
  summary: AssetSummary;
  sealed_product_metadata: SealedProductMetadata | null;
}

export type SealedProductAsset = AssetResponse & {
  asset_type: "sealed_product";
  sealed_product_metadata: SealedProductMetadata;
};

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

export interface PurchaseLotCreatePayload {
  purchase_date: string;
  quantity: number;
  purchase_price_per_unit: string;
  currency: "CAD";
}

export function isSealedProductAsset(
  asset: AssetResponse,
): asset is SealedProductAsset {
  return (
    asset.asset_type === "sealed_product" &&
    asset.sealed_product_metadata !== null
  );
}

export function getSealedProductTypeLabel(type: SealedProductType): string {
  return (
    SEALED_PRODUCT_TYPE_OPTIONS.find((option) => option.value === type)?.label ??
    type
  );
}
