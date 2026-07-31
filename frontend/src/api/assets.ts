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

export function listAssets(): Promise<AssetResponse[]> {
  return requestJson<AssetResponse[]>("/api/assets");
}

export function getAsset(assetId: number): Promise<AssetResponse> {
  return requestJson<AssetResponse>(`/api/assets/${assetId}`);
}

export function createAsset(
  payload: AssetCreatePayload,
): Promise<AssetResponse> {
  return requestJson<AssetResponse>("/api/assets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function createSealedProduct(
  payload: SealedProductCreatePayload,
): Promise<AssetResponse> {
  return createAsset(payload);
}

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

export function deletePurchaseLot(lotId: number): Promise<void> {
  return requestNoContent(`/api/purchase-lots/${lotId}`, {
    method: "DELETE",
  });
}

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
