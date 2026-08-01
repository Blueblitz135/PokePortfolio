import { Link } from "react-router-dom";

import {
  getAssetTypeLabel,
  getSealedProductTypeLabel,
  type AssetResponse,
} from "../types/assets";
import { useCurrencyFormatter } from "../hooks/useCurrencyFormatter";
import { formatPercent } from "../utils/formatters";

interface CollectionAssetCardProps {
  asset: AssetResponse;
  showDetailsLink?: boolean;
}

function formatCardNumber(asset: AssetResponse): string | null {
  const metadata = asset.card_metadata;

  if (metadata === null) {
    return null;
  }

  return metadata.set_total
    ? `${metadata.card_number}/${metadata.set_total}`
    : metadata.card_number;
}

function getAssetDetails(asset: AssetResponse): string[] {
  if (asset.asset_type === "raw_card") {
    return [
      asset.card_metadata?.set_name,
      formatCardNumber(asset),
      asset.raw_details?.condition,
    ].filter((value): value is string => Boolean(value));
  }

  if (asset.asset_type === "graded_card") {
    const grade = asset.graded_details
      ? `${asset.graded_details.grading_company} ${asset.graded_details.grade}`
      : null;

    return [
      grade,
      asset.card_metadata?.set_name,
      formatCardNumber(asset),
    ].filter((value): value is string => Boolean(value));
  }

  const metadata = asset.sealed_product_metadata;
  return [
    metadata ? getSealedProductTypeLabel(metadata.sealed_product_type) : null,
    metadata?.set_name,
    metadata?.year?.toString(),
  ].filter((value): value is string => Boolean(value));
}

function getPerformanceClass(value: string | null): string {
  if (value === null) {
    return "";
  }

  const amount = Number(value);
  if (!Number.isFinite(amount) || amount === 0) {
    return "";
  }

  return amount > 0 ? "metric-value--positive" : "metric-value--negative";
}

export function CollectionAssetCard({
  asset,
  showDetailsLink = true,
}: CollectionAssetCardProps) {
  const formatCurrency = useCurrencyFormatter();
  const details = getAssetDetails(asset);
  const marketPriceUnavailable =
    asset.summary.market_price_per_unit === null;
  const profitLossClass = getPerformanceClass(asset.summary.profit_loss);
  const roiClass = getPerformanceClass(asset.summary.roi_percent);
  const image = (
    <img
      className="collection-card-image"
      src={asset.primary_image_url}
      alt={asset.display_name}
      loading="lazy"
      onError={(event) => {
        event.currentTarget.onerror = null;
        event.currentTarget.src = "/static/placeholders/asset.svg";
      }}
    />
  );

  return (
    <article
      className={`collection-card collection-card--${asset.asset_type}`}
      id={`asset-${asset.id}`}
    >
      <div className="collection-card-header">
        {asset.asset_type === "graded_card" ? (
          <div className="graded-card-image">
            <div className="graded-card-label">
              <span>
                {asset.graded_details?.grading_company ?? "Graded"}
              </span>
              <strong>{asset.graded_details?.grade ?? "—"}</strong>
            </div>
            {image}
          </div>
        ) : (
          image
        )}
        <div className="collection-card-copy">
          <span className="asset-type-badge">
            {getAssetTypeLabel(asset.asset_type)}
          </span>
          <h3>{asset.display_name}</h3>
          {details.length > 0 && (
            <p className="asset-description">{details.join(" · ")}</p>
          )}
        </div>
      </div>

      <dl className="dashboard-metrics">
        <div>
          <dt>Total quantity</dt>
          <dd>{asset.summary.total_quantity}</dd>
        </div>
        <div>
          <dt>Average cost</dt>
          <dd>
            {formatCurrency(
              asset.summary.average_cost_per_unit,
              asset.summary.currency,
            )}
          </dd>
        </div>
        <div>
          <dt>Latest market price</dt>
          <dd>
            {formatCurrency(
              asset.summary.market_price_per_unit,
              asset.summary.currency,
            )}
          </dd>
        </div>
        <div>
          <dt>Total market value</dt>
          <dd>
            {formatCurrency(
              asset.summary.total_market_value,
              asset.summary.currency,
            )}
          </dd>
        </div>
        <div>
          <dt>Profit / loss</dt>
          <dd className={profitLossClass}>
            {formatCurrency(
              asset.summary.profit_loss,
              asset.summary.currency,
            )}
          </dd>
        </div>
        <div>
          <dt>ROI</dt>
          <dd className={roiClass}>
            {formatPercent(asset.summary.roi_percent)}
          </dd>
        </div>
      </dl>

      {marketPriceUnavailable && (
        <p className="market-unavailable">
          Market price not available yet.
        </p>
      )}

      {showDetailsLink && (
        <Link className="card-action" to={`/assets/${asset.id}`}>
          Open asset details <span aria-hidden="true">→</span>
        </Link>
      )}
    </article>
  );
}
