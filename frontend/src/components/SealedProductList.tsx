import {
  getSealedProductTypeLabel,
  type SealedProductAsset,
} from "../types/assets";

interface SealedProductListProps {
  assets: SealedProductAsset[];
  selectedAssetId: number | null;
  isLoading: boolean;
  error: string | null;
  onSelect: (assetId: number) => void;
}

export function SealedProductList({
  assets,
  selectedAssetId,
  isLoading,
  error,
  onSelect,
}: SealedProductListProps) {
  if (isLoading) {
    return <p className="state-message">Loading sealed products...</p>;
  }

  if (error) {
    return (
      <p className="state-message state-message--error" role="alert">
        {error}
      </p>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="empty-state">
        <h3>No sealed products yet</h3>
        <p>Add your first sealed product using the form.</p>
      </div>
    );
  }

  return (
    <div className="asset-list">
      {assets.map((asset) => (
        <button
          className={`asset-list-item ${
            selectedAssetId === asset.id ? "asset-list-item--selected" : ""
          }`}
          type="button"
          key={asset.id}
          onClick={() => onSelect(asset.id)}
          aria-pressed={selectedAssetId === asset.id}
        >
          <img
            src={asset.primary_image_url}
            alt=""
            className="asset-list-image"
          />
          <span className="asset-list-copy">
            <strong>{asset.display_name}</strong>
            <span>
              {getSealedProductTypeLabel(
                asset.sealed_product_metadata.sealed_product_type,
              )}
            </span>
            <span>
              {asset.summary.total_quantity}{" "}
              {asset.summary.total_quantity === 1 ? "unit" : "units"}
            </span>
          </span>
        </button>
      ))}
    </div>
  );
}
