import type {
  AssetImage,
  AssetResponse,
  PurchaseLot,
  PurchaseLotCreatePayload,
  SealedProductCreatePayload,
} from "../types/assets";

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };

    if (typeof body.detail === "string") {
      return body.detail;
    }

    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }
          return null;
        })
        .filter((message): message is string => message !== null);

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    // Use the status-based fallback when the response does not contain JSON.
  }

  return `The request failed with status ${response.status}.`;
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

export function listAssets(): Promise<AssetResponse[]> {
  return request<AssetResponse[]>("/api/assets");
}

export function getAsset(assetId: number): Promise<AssetResponse> {
  return request<AssetResponse>(`/api/assets/${assetId}`);
}

export function createSealedProduct(
  payload: SealedProductCreatePayload,
): Promise<AssetResponse> {
  return request<AssetResponse>("/api/assets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function createPurchaseLot(
  assetId: number,
  payload: PurchaseLotCreatePayload,
): Promise<PurchaseLot> {
  return request<PurchaseLot>(`/api/assets/${assetId}/purchase-lots`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function uploadAssetImage(
  assetId: number,
  file: File,
): Promise<AssetImage> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("is_primary", "true");

  return request<AssetImage>(`/api/assets/${assetId}/images`, {
    method: "POST",
    body: formData,
  });
}
