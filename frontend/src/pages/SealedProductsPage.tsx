import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAsset, listAssets } from "../api/assets";
import { getHealth } from "../api/health";
import { ApiStatus } from "../components/ApiStatus";
import { SealedProductDetail } from "../components/SealedProductDetail";
import { SealedProductForm } from "../components/SealedProductForm";
import { SealedProductList } from "../components/SealedProductList";
import {
  isSealedProductAsset,
  type SealedProductAsset,
} from "../types/assets";

type ApiState = "loading" | "online" | "offline";

export function SealedProductsPage() {
  const [apiState, setApiState] = useState<ApiState>("loading");
  const [sealedProducts, setSealedProducts] = useState<SealedProductAsset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
  const [isLoadingAssets, setIsLoadingAssets] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadSealedProducts = useCallback(async () => {
    setIsLoadingAssets(true);
    setLoadError(null);

    try {
      const assets = await listAssets();
      const sealedAssets = assets.filter(isSealedProductAsset);
      setSealedProducts(sealedAssets);
      setSelectedAssetId((currentId) => {
        if (sealedAssets.some((asset) => asset.id === currentId)) {
          return currentId;
        }
        return sealedAssets[0]?.id ?? null;
      });
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "The sealed products could not be loaded.",
      );
    } finally {
      setIsLoadingAssets(false);
    }
  }, []);

  useEffect(() => {
    getHealth()
      .then(() => setApiState("online"))
      .catch(() => setApiState("offline"));

    void loadSealedProducts();
  }, [loadSealedProducts]);

  function handleCreated(asset: SealedProductAsset) {
    setSealedProducts((currentAssets) => [...currentAssets, asset]);
    setSelectedAssetId(asset.id);
    setLoadError(null);
  }

  async function refreshAsset(assetId: number) {
    const refreshedAsset = await getAsset(assetId);

    if (!isSealedProductAsset(refreshedAsset)) {
      throw new Error("The API returned an unexpected asset type.");
    }

    setSealedProducts((currentAssets) =>
      currentAssets.map((asset) =>
        asset.id === refreshedAsset.id ? refreshedAsset : asset,
      ),
    );
  }

  const selectedAsset =
    sealedProducts.find((asset) => asset.id === selectedAssetId) ?? null;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <Link className="back-link" to="/collection">
            ← Back to collection
          </Link>
          <p className="eyebrow">Pokémon Portfolio</p>
          <h1>Sealed product collection</h1>
          <p className="intro">
            Record sealed products, their purchase lots, and a primary product
            image.
          </p>
        </div>
        <ApiStatus status={apiState} />
      </header>

      <div className="workspace-grid">
        <div className="sidebar-stack">
          <div id="add-sealed-product">
            <SealedProductForm onCreated={handleCreated} />
          </div>

          <section
            className="panel collection-panel"
            aria-labelledby="sealed-products-title"
          >
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Collection</p>
                <h2 id="sealed-products-title">Your sealed products</h2>
              </div>
              {!isLoadingAssets && !loadError && (
                <span className="asset-count">{sealedProducts.length}</span>
              )}
            </div>

            <SealedProductList
              assets={sealedProducts}
              selectedAssetId={selectedAssetId}
              isLoading={isLoadingAssets}
              error={loadError}
              onSelect={setSelectedAssetId}
            />
          </section>
        </div>

        <SealedProductDetail
          asset={selectedAsset}
          onRefresh={refreshAsset}
        />
      </div>
    </div>
  );
}
