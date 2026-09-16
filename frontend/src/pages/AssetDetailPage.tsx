/** Load one route-selected asset and render its detail, loading, or error state. */
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { refreshAssetPrice } from "../api/assets";
import { AssetDetailView } from "../components/AssetDetailView";
import type { AssetResponse } from "../types/assets";

/** Accept only positive integer route identifiers. */
function parseAssetId(value: string | undefined): number | null {
  if (!value || !/^[1-9]\d*$/.test(value)) {
    return null;
  }

  const parsedValue = Number(value);
  return Number.isSafeInteger(parsedValue) ? parsedValue : null;
}

/** Coordinate asset fetching and refreshes requested by nested editors. */
export function AssetDetailPage() {
  const { assetId: assetIdParam } = useParams();
  const assetId = parseAssetId(assetIdParam);
  const [asset, setAsset] = useState<AssetResponse | null>(null);
  const [loadError, setLoadError] = useState<{
    assetId: number;
    message: string;
  } | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);
  const currentAssetIdRef = useRef(assetId);
  currentAssetIdRef.current = assetId;

  useEffect(() => {
    if (assetId === null) {
      setAsset(null);
      setLoadError(null);
      return;
    }

    let isCurrentRequest = true;
    setAsset(null);
    setLoadError(null);

    refreshAssetPrice(assetId)
      .then((loadedAsset) => {
        if (isCurrentRequest) {
          setAsset(loadedAsset);
        }
      })
      .catch((loadError: unknown) => {
        if (isCurrentRequest) {
          setLoadError({
            assetId,
            message:
              loadError instanceof Error
                ? loadError.message
                : "The asset could not be loaded.",
          });
        }
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [assetId, requestVersion]);

  const refreshAsset = useCallback(async () => {
    if (assetId === null) {
      throw new Error("The asset ID is invalid.");
    }

    const refreshedAsset = await refreshAssetPrice(assetId);
    if (currentAssetIdRef.current === assetId) {
      setAsset(refreshedAsset);
      setLoadError(null);
    }
  }, [assetId]);

  const currentAsset =
    assetId !== null && asset?.id === assetId ? asset : null;
  const currentError =
    assetId === null
      ? "The asset ID in this address is invalid."
      : loadError?.assetId === assetId
        ? loadError.message
        : null;
  const isLoading =
    assetId !== null && currentAsset === null && currentError === null;

  return (
    <div className="app-shell asset-detail-page">
      <Link className="back-link" to="/collection">
        ← Back to collection
      </Link>

      {isLoading && (
        <section className="panel detail-page-state" role="status">
          <p className="eyebrow">Asset details</p>
          <h1>Loading asset...</h1>
          <p className="intro">Retrieving metadata and purchase history.</p>
        </section>
      )}

      {!isLoading && currentError && (
        <section className="panel detail-page-state" role="alert">
          <p className="eyebrow">Asset details</p>
          <h1>Asset unavailable</h1>
          <p className="intro">{currentError}</p>
          {assetId !== null && (
            <button
              className="secondary-button"
              type="button"
              onClick={() => {
                setLoadError(null);
                setRequestVersion((current) => current + 1);
              }}
            >
              Try again
            </button>
          )}
        </section>
      )}

      {!isLoading && currentAsset && (
        <>
          <button className="secondary-button" onClick={() => setRequestVersion((value) => value + 1)}>Refresh market price</button>
          <AssetDetailView asset={currentAsset} onRefresh={refreshAsset} />
        </>
      )}
    </div>
  );
}
