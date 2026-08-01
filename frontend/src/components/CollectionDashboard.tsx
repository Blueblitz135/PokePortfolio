import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import type { AssetResponse } from "../types/assets";
import {
  AssetTypeFilter,
  type AssetFilter,
} from "./AssetTypeFilter";
import { CollectionAssetCard } from "./CollectionAssetCard";

interface CollectionDashboardProps {
  assets: AssetResponse[];
  initialFilter: AssetFilter;
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
}

export function CollectionDashboard({
  assets,
  initialFilter,
  isLoading,
  error,
  onRetry,
}: CollectionDashboardProps) {
  const [selectedFilter, setSelectedFilter] = useState<AssetFilter>(
    () => initialFilter,
  );

  const counts = useMemo<Record<AssetFilter, number>>(
    () => ({
      all: assets.length,
      raw_card: assets.filter((asset) => asset.asset_type === "raw_card")
        .length,
      graded_card: assets.filter(
        (asset) => asset.asset_type === "graded_card",
      ).length,
      sealed_product: assets.filter(
        (asset) => asset.asset_type === "sealed_product",
      ).length,
    }),
    [assets],
  );

  const visibleAssets =
    selectedFilter === "all"
      ? assets
      : assets.filter((asset) => asset.asset_type === selectedFilter);

  return (
    <section className="dashboard-panel" aria-labelledby="collection-title">
      <div className="dashboard-toolbar">
        <div>
          <p className="eyebrow">Collection</p>
          <h2 id="collection-title">Your assets</h2>
          {!isLoading && !error && assets.length > 0 && (
            <p className="collection-count">
              Showing {visibleAssets.length} of {assets.length}
            </p>
          )}
        </div>
        <Link
          className="primary-button button-link"
          to="/sealed-products#add-sealed-product"
        >
          Add sealed product
        </Link>
      </div>

      {!isLoading && !error && assets.length > 0 && (
        <AssetTypeFilter
          selectedFilter={selectedFilter}
          counts={counts}
          onChange={setSelectedFilter}
        />
      )}

      {isLoading && (
        <p className="state-message" role="status">
          Loading your collection...
        </p>
      )}

      {!isLoading && error && (
        <div className="state-message state-message--error" role="alert">
          <p>{error}</p>
          <button className="secondary-button" type="button" onClick={onRetry}>
            Try again
          </button>
        </div>
      )}

      {!isLoading && !error && assets.length === 0 && (
        <div className="empty-state dashboard-empty-state">
          <h3>Your collection is empty</h3>
          <p>No assets yet. Add your first card or sealed product.</p>
          <Link
            className="primary-button button-link"
            to="/sealed-products#add-sealed-product"
          >
            Add a sealed product
          </Link>
        </div>
      )}

      {!isLoading &&
        !error &&
        assets.length > 0 &&
        visibleAssets.length === 0 && (
          <div className="empty-state dashboard-empty-state">
            <h3>No assets in this category</h3>
            <p>Choose another filter to see the rest of your collection.</p>
            <button
              className="secondary-button"
              type="button"
              onClick={() => setSelectedFilter("all")}
            >
              Show all assets
            </button>
          </div>
        )}

      {!isLoading && !error && visibleAssets.length > 0 && (
        <div className="collection-grid">
          {visibleAssets.map((asset) => (
            <CollectionAssetCard key={asset.id} asset={asset} />
          ))}
        </div>
      )}
    </section>
  );
}
