import { AssetImageUpload } from "./AssetImageUpload";
import { PurchaseLotForm } from "./PurchaseLotForm";
import {
  getSealedProductTypeLabel,
  type SealedProductAsset,
} from "../types/assets";

interface SealedProductDetailProps {
  asset: SealedProductAsset | null;
  onRefresh: (assetId: number) => Promise<void>;
}

function formatCad(value: string | null): string {
  if (value === null) {
    return "Not available";
  }

  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return value;
  }

  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
  }).format(amount);
}

function formatPurchaseDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-CA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatPokemonCenterStatus(value: boolean | null): string {
  if (value === null) {
    return "Not provided";
  }
  return value ? "Exclusive" : "No";
}

export function SealedProductDetail({
  asset,
  onRefresh,
}: SealedProductDetailProps) {
  if (!asset) {
    return (
      <section className="panel detail-panel empty-state">
        <h2>Select a sealed product</h2>
        <p>Choose a product to view its purchase history and add an image.</p>
      </section>
    );
  }

  const metadata = asset.sealed_product_metadata;
  const refreshSelectedAsset = () => onRefresh(asset.id);

  return (
    <article className="panel detail-panel">
      <header className="asset-detail-header">
        <img
          className="asset-detail-image"
          src={asset.primary_image_url}
          alt={asset.display_name}
        />
        <div>
          <p className="eyebrow">Sealed product</p>
          <h2>{asset.display_name}</h2>
          <p className="asset-type-badge">
            {getSealedProductTypeLabel(metadata.sealed_product_type)}
          </p>
          {asset.user_note && <p className="asset-note">{asset.user_note}</p>}
        </div>
      </header>

      <section className="detail-section" aria-labelledby="metadata-title">
        <h3 id="metadata-title">Product details</h3>
        <dl className="metadata-grid">
          <div>
            <dt>Product</dt>
            <dd>{metadata.product_name}</dd>
          </div>
          <div>
            <dt>Set</dt>
            <dd>{metadata.set_name ?? "Not provided"}</dd>
          </div>
          <div>
            <dt>Year</dt>
            <dd>{metadata.year ?? "Not provided"}</dd>
          </div>
          <div>
            <dt>Pokémon Center</dt>
            <dd>
              {formatPokemonCenterStatus(
                metadata.is_pokemon_center_exclusive,
              )}
            </dd>
          </div>
        </dl>
      </section>

      <section className="detail-section" aria-labelledby="summary-title">
        <h3 id="summary-title">Ownership summary</h3>
        <div className="summary-grid">
          <div className="summary-card">
            <span>Total quantity</span>
            <strong>{asset.summary.total_quantity}</strong>
          </div>
          <div className="summary-card">
            <span>Total cost</span>
            <strong>{formatCad(asset.summary.total_cost)}</strong>
          </div>
          <div className="summary-card">
            <span>Average cost</span>
            <strong>
              {formatCad(asset.summary.average_cost_per_unit)}
              {asset.summary.average_cost_per_unit !== null && " / unit"}
            </strong>
          </div>
        </div>
      </section>

      <section className="detail-section" aria-labelledby="lots-title">
        <h3 id="lots-title">Purchase lots</h3>
        {asset.purchase_lots.length === 0 ? (
          <p className="inline-empty-state">
            No purchase lots yet. Add the first purchase below.
          </p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Quantity</th>
                  <th>Price per unit</th>
                </tr>
              </thead>
              <tbody>
                {asset.purchase_lots.map((lot) => (
                  <tr key={lot.id}>
                    <td>{formatPurchaseDate(lot.purchase_date)}</td>
                    <td>{lot.quantity}</td>
                    <td>{formatCad(lot.purchase_price_per_unit)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <PurchaseLotForm
        key={`lot-${asset.id}`}
        assetId={asset.id}
        onSaved={refreshSelectedAsset}
      />
      <AssetImageUpload
        key={`image-${asset.id}`}
        assetId={asset.id}
        onSaved={refreshSelectedAsset}
      />
    </article>
  );
}
