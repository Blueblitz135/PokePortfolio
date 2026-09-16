/** Typed HTTP operations for assets and their nested portfolio records. */
import type {
  AssetCreatePayload,
  AssetImage,
  AssetResponse,
  ManualPriceSnapshotCreatePayload,
  PriceSnapshot,
  PurchaseLot,
  PurchaseLotCreatePayload,
  PurchaseLotUpdatePayload,
  SealedProductCreatePayload,
} from "../types/assets";
import { requestJson, requestNoContent } from "./client";

/** Fetch every hydrated portfolio asset. */
export function listAssets(): Promise<AssetResponse[]> {
  return requestJson<AssetResponse[]>("/api/assets");
}

/** Fetch current card prices and recompute all collection values. */
export function refreshMarketPrices(): Promise<AssetResponse[]> {
  return requestJson<AssetResponse[]>("/api/assets/refresh-prices", { method: "POST" });
}

export function refreshAssetPrice(assetId: number): Promise<AssetResponse> {
  return requestJson<AssetResponse>(`/api/assets/${assetId}/refresh-price`, { method: "POST" });
}

/** Fetch one hydrated asset by database identifier. */
export function getAsset(assetId: number): Promise<AssetResponse> {
  return requestJson<AssetResponse>(`/api/assets/${assetId}`);
}

/** Create a raw, graded, or sealed asset using its discriminated payload. */
export function createAsset(
  payload: AssetCreatePayload,
): Promise<AssetResponse> {
  return requestJson<AssetResponse>("/api/assets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Convenience wrapper for creating a sealed-product asset. */
export function createSealedProduct(
  payload: SealedProductCreatePayload,
): Promise<AssetResponse> {
  return createAsset(payload);
}

/** Record another acquisition lot beneath an asset. */
export function createPurchaseLot(
  assetId: number,
  payload: PurchaseLotCreatePayload,
): Promise<PurchaseLot> {
  return requestJson<PurchaseLot>(`/api/assets/${assetId}/purchase-lots`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Partially update a purchase lot. */
export function updatePurchaseLot(
  lotId: number,
  payload: PurchaseLotUpdatePayload,
): Promise<PurchaseLot> {
  return requestJson<PurchaseLot>(`/api/purchase-lots/${lotId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Delete one purchase lot. */
export function deletePurchaseLot(lotId: number): Promise<void> {
  return requestNoContent(`/api/purchase-lots/${lotId}`, {
    method: "DELETE",
  });
}

/** Save a user-entered market price against an asset. */
export function createManualPriceSnapshot(
  assetId: number,
  payload: ManualPriceSnapshotCreatePayload,
): Promise<PriceSnapshot> {
  return requestJson<PriceSnapshot>(
    `/api/assets/${assetId}/price-snapshots`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

/** Upload an image as multipart form data and optionally make it primary. */
export function uploadAssetImage(
  assetId: number,
  file: File,
): Promise<AssetImage> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("is_primary", "true");

  return requestJson<AssetImage>(`/api/assets/${assetId}/images`, {
    method: "POST",
    body: formData,
  });
}
