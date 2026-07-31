import { useEffect, useState } from "react";

import type { AssetResponse } from "../types/assets";
import {
  getAssetTypeLabel,
  getSealedProductTypeLabel,
} from "../types/assets";
import { formatCurrency, formatPercent } from "../utils/formatters";
import { AssetImageUpload } from "./AssetImageUpload";
import { ManualPriceSnapshotForm } from "./ManualPriceSnapshotForm";
import { PurchaseLotForm } from "./PurchaseLotForm";
import { PurchaseLotManager } from "./PurchaseLotManager";

interface AssetDetailViewProps {
  asset: AssetResponse;
  onRefresh: () => Promise<void>;
}

interface MetadataItem {
  label: string;
  value: string;
}

const PLACEHOLDER_IMAGE_URL = "/static/placeholders/asset.svg";

function optionalValue(value: string | number | null | undefined): string {
  return value === null || value === undefined || value === ""
    ? "Not provided"
    : String(value);
}

function formatCardNumber(asset: AssetResponse): string {
  const metadata = asset.card_metadata;
  if (metadata === null) {
    return "Not provided";
  }

  return metadata.set_total
    ? `${metadata.card_number}/${metadata.set_total}`
    : metadata.card_number;
}

function getMetadata(asset: AssetResponse): {
  title: string;
  items: MetadataItem[];
} {
  if (asset.asset_type === "sealed_product") {
    const metadata = asset.sealed_product_metadata;
    return {
      title: "Product metadata",
      items: [
        { label: "Product", value: optionalValue(metadata?.product_name) },
        {
          label: "Product type",
          value: metadata
            ? getSealedProductTypeLabel(metadata.sealed_product_type)
            : "Not provided",
        },
        { label: "Set", value: optionalValue(metadata?.set_name) },
        { label: "Year", value: optionalValue(metadata?.year) },
        {
          label: "Pokémon Center",
          value:
            metadata?.is_pokemon_center_exclusive === null ||
            metadata?.is_pokemon_center_exclusive === undefined
              ? "Not provided"
              : metadata.is_pokemon_center_exclusive
                ? "Exclusive"
                : "No",
        },
      ],
    };
  }

  const metadata = asset.card_metadata;
  const items: MetadataItem[] = [
    { label: "Card name", value: optionalValue(metadata?.name) },
    { label: "Set", value: optionalValue(metadata?.set_name) },
    { label: "Card number", value: formatCardNumber(asset) },
    { label: "Year", value: optionalValue(metadata?.year) },
    { label: "Rarity", value: optionalValue(metadata?.rarity) },
    { label: "Variant", value: optionalValue(metadata?.variant) },
  ];

  if (asset.asset_type === "raw_card") {
    items.push({
      label: "Condition",
      value: optionalValue(asset.raw_details?.condition),
    });
  } else {
    items.push(
      {
        label: "Grading company",
        value: optionalValue(asset.graded_details?.grading_company),
      },
      { label: "Grade", value: optionalValue(asset.graded_details?.grade) },
      {
        label: "Certification number",
        value: optionalValue(asset.graded_details?.cert_number),
      },
    );
  }

  return {
    title:
      asset.asset_type === "raw_card"
        ? "Raw card metadata"
        : "Graded card metadata",
    items,
  };
}

function getPreferredImageUrl(asset: AssetResponse): string {
  if (asset.primary_image_url !== PLACEHOLDER_IMAGE_URL) {
    return asset.primary_image_url;
  }

  return (
    asset.card_metadata?.image_url ??
    asset.sealed_product_metadata?.image_url ??
    PLACEHOLDER_IMAGE_URL
  );
}

function getMetadataImageUrl(asset: AssetResponse): string | null {
  return (
    asset.card_metadata?.image_url ??
    asset.sealed_product_metadata?.image_url ??
    null
  );
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

function AssetHeroImage({ asset }: { asset: AssetResponse }) {
  const preferredImageUrl = getPreferredImageUrl(asset);
  const metadataImageUrl = getMetadataImageUrl(asset);
  const [imageUrl, setImageUrl] = useState(preferredImageUrl);

  useEffect(() => {
    setImageUrl(preferredImageUrl);
  }, [preferredImageUrl]);

  const image = (
    <img
      className="asset-detail-image"
      src={imageUrl}
      alt={asset.display_name}
      onError={() =>
        setImageUrl((failedUrl) =>
          failedUrl === asset.primary_image_url &&
          metadataImageUrl !== null &&
          metadataImageUrl !== failedUrl
            ? metadataImageUrl
            : PLACEHOLDER_IMAGE_URL,
        )
      }
    />
  );

  return (
    <figure className="asset-detail-visual">
      {asset.asset_type === "graded_card" ? (
        <div className="asset-detail-graded-image">
          <div className="graded-card-label">
            <span>
              {asset.graded_details?.grading_company ?? "Graded card"}
            </span>
            <strong>{asset.graded_details?.grade ?? "—"}</strong>
          </div>
          {image}
        </div>
      ) : (
        image
      )}
      <figcaption className="asset-detail-image-caption">
        {imageUrl === PLACEHOLDER_IMAGE_URL
          ? "No image available yet."
          : "Asset image"}
      </figcaption>
    </figure>
  );
}

export function AssetDetailView({
  asset,
  onRefresh,
}: AssetDetailViewProps) {
  const metadata = getMetadata(asset);
  const profitLossClass = getPerformanceClass(asset.summary.profit_loss);
  const roiClass = getPerformanceClass(asset.summary.roi_percent);
  const userNote = asset.user_note?.trim() ?? "";

  return (
    <article className="panel detail-panel asset-detail-page-panel">
      <header className="asset-detail-header">
        <AssetHeroImage asset={asset} />
        <div>
          <p className="eyebrow">Asset details</p>
          <h1>{asset.display_name}</h1>
          <span className="asset-type-badge">
            {getAssetTypeLabel(asset.asset_type)}
          </span>
        </div>
      </header>

      <section className="detail-section" aria-labelledby="asset-note-title">
        <h2 id="asset-note-title">Note</h2>
        <p className={`asset-note ${userNote ? "" : "asset-note--empty"}`}>
          {userNote || "No note added."}
        </p>
      </section>

      <section className="detail-section" aria-labelledby="metadata-title">
        <h2 id="metadata-title">{metadata.title}</h2>
        <dl className="metadata-grid">
          {metadata.items.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="detail-section" aria-labelledby="summary-title">
        <h2 id="summary-title">Portfolio summary</h2>
        <div className="summary-grid asset-summary-grid">
          <div className="summary-card">
            <span>Total quantity</span>
            <strong>{asset.summary.total_quantity}</strong>
          </div>
          <div className="summary-card">
            <span>Total cost</span>
            <strong>
              {formatCurrency(
                asset.summary.total_cost,
                asset.summary.currency,
              )}
            </strong>
          </div>
          <div className="summary-card">
            <span>Average cost</span>
            <strong>
              {formatCurrency(
                asset.summary.average_cost_per_unit,
                asset.summary.currency,
              )}
            </strong>
          </div>
          <div className="summary-card">
            <span>Latest market price</span>
            <strong>
              {formatCurrency(
                asset.summary.market_price_per_unit,
                asset.summary.currency,
              )}
            </strong>
          </div>
          <div className="summary-card">
            <span>Total market value</span>
            <strong>
              {formatCurrency(
                asset.summary.total_market_value,
                asset.summary.currency,
              )}
            </strong>
          </div>
          <div className="summary-card">
            <span>Profit / loss</span>
            <strong className={profitLossClass}>
              {formatCurrency(
                asset.summary.profit_loss,
                asset.summary.currency,
              )}
            </strong>
          </div>
          <div className="summary-card">
            <span>ROI</span>
            <strong className={roiClass}>
              {formatPercent(asset.summary.roi_percent)}
            </strong>
          </div>
        </div>
        {asset.summary.market_price_per_unit === null && (
          <p className="market-unavailable">
            Market price not available yet.
          </p>
        )}
      </section>

      <ManualPriceSnapshotForm
        key={`price-${asset.id}`}
        assetId={asset.id}
        latestSnapshot={asset.latest_price_snapshot}
        onSaved={onRefresh}
      />

      <section
        className="detail-section purchase-history-section"
        aria-labelledby="purchase-lots-title"
      >
        <h2 id="purchase-lots-title" tabIndex={-1}>
          Purchase lots
        </h2>
        <PurchaseLotManager
          key={`lots-${asset.id}`}
          assetName={asset.display_name}
          lots={asset.purchase_lots}
          onChanged={onRefresh}
        />
        <PurchaseLotForm
          key={`add-lot-${asset.id}`}
          assetId={asset.id}
          onSaved={onRefresh}
        />
      </section>

      <section
        className="detail-section asset-images-section"
        aria-labelledby="asset-images-title"
      >
        <h2 id="asset-images-title">Images</h2>
        <AssetImageUpload
          key={`image-${asset.id}`}
          assetId={asset.id}
          onSaved={onRefresh}
        />
      </section>
    </article>
  );
}
