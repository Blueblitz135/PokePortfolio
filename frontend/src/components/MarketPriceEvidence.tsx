import type { AssetResponse } from "../types/assets";
import { useCurrencyFormatter } from "../hooks/useCurrencyFormatter";

/** Show pricing provenance and coverage without presenting missing prices as zero. */
export function MarketPriceEvidence({ asset, detailed = false }: { asset: AssetResponse; detailed?: boolean }) {
  const formatCurrency = useCurrencyFormatter();
  const pricing = asset.market_pricing;
  if (!pricing) return null;
  return (
    <div className="market-price-evidence">
      <p role="status">{pricing.detail}</p>
      {pricing.state === "available" && (
        <p><a href={pricing.source_url} target="_blank" rel="noreferrer">{pricing.source}</a>
          {pricing.observed_at && <> · Price observed {new Date(pricing.observed_at).toLocaleString()}</>}
          <br />USD prices converted to CAD before portfolio calculations.
        </p>
      )}
      {detailed && pricing.tcgplayer && (
        <section aria-label="TCGPlayer reference prices">
          <h3>TCGPlayer reference prices</h3>
          <p>{pricing.tcgplayer.note}</p>
          {pricing.tcgplayer.observed_at && <p>Updated {new Date(pricing.tcgplayer.observed_at).toLocaleString()}</p>}
          {pricing.tcgplayer.variants.map((variant) => (
            <div key={variant.printing}>
              <h4>{variant.printing}</h4>
              <dl className="dashboard-metrics">
                <div><dt>Market</dt><dd>{formatCurrency(variant.market_price_cad, "CAD")}</dd></div>
                <div><dt>Low</dt><dd>{formatCurrency(variant.low_price_cad, "CAD")}</dd></div>
                <div><dt>Median</dt><dd>{formatCurrency(variant.median_price_cad, "CAD")}</dd></div>
                <div><dt>High</dt><dd>{formatCurrency(variant.high_price_cad, "CAD")}</dd></div>
              </dl>
            </div>
          ))}
          {pricing.tcgplayer.state !== "available" && <p>TCGPlayer prices are unavailable for this card.</p>}
        </section>
      )}
    </div>
  );
}
