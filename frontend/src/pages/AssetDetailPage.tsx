/** Load one route-selected asset and render its detail, loading, or error state. */
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { deleteAsset, refreshAssetPrice } from "../api/assets";
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
  const navigate = useNavigate();
  const { assetId: assetIdParam } = useParams();
  const assetId = parseAssetId(assetIdParam);
  const [asset, setAsset] = useState<AssetResponse | null>(null);
  const [loadError, setLoadError] = useState<{
    assetId: number;
    message: string;
  } | null>(null);
  const [requestVersion, setRequestVersion] = useState(0);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
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

  async function handleDeleteAsset() {
    if (currentAsset === null || isDeleting) {
      return;
    }

    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteAsset(currentAsset.id);
      navigate("/collection", { replace: true });
    } catch (error) {
      setDeleteError(
        error instanceof Error
          ? error.message
          : "The asset could not be deleted.",
      );
      setIsDeleting(false);
    }
  }

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
          <div className="asset-detail-actions">
            <button className="secondary-button" onClick={() => setRequestVersion((value) => value + 1)}>Refresh market price</button>
            <button
              className="danger-button"
              type="button"
              onClick={() => {
                setIsConfirmingDelete(true);
                setDeleteError(null);
              }}
            >
              Delete asset
            </button>
          </div>
          {isConfirmingDelete && (
            <section className="asset-delete-confirmation" role="alert">
              <h2>Delete {currentAsset.display_name}?</h2>
              <p>
                This permanently removes the asset, its purchase lots, images,
                and saved price history from this collection.
              </p>
              {deleteError && (
                <p className="form-message form-message--error">{deleteError}</p>
              )}
              <div className="asset-detail-actions">
                <button
                  className="danger-button"
                  type="button"
                  disabled={isDeleting}
                  onClick={() => void handleDeleteAsset()}
                >
                  {isDeleting ? "Deleting asset..." : "Yes, delete asset"}
                </button>
                <button
                  className="secondary-button"
                  type="button"
                  disabled={isDeleting}
                  onClick={() => {
                    setIsConfirmingDelete(false);
                    setDeleteError(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </section>
          )}
          <AssetDetailView asset={currentAsset} onRefresh={refreshAsset} />
        </>
      )}
    </div>
  );
}
