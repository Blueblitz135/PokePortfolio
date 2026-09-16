/** Load the portfolio and coordinate filtering, dashboard, cards, and analyst UI. */
import { useCallback, useEffect, useState } from "react";

import { listAssets, refreshMarketPrices } from "../api/assets";
import { getHealth } from "../api/health";
import { ApiStatus } from "../components/ApiStatus";
import { CollectionDashboard } from "../components/CollectionDashboard";
import { PortfolioChatbot } from "../components/PortfolioChatbot";
import { usePortfolioPreferences } from "../hooks/usePortfolioPreferences";
import type { AssetResponse } from "../types/assets";

type ApiState = "loading" | "online" | "offline";

/** Render the main collection with explicit loading, empty, and error states. */
export function CollectionPage() {
  const { preferences } = usePortfolioPreferences();
  const [apiState, setApiState] = useState<ApiState>("loading");
  const [assets, setAssets] = useState<AssetResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [priceError, setPriceError] = useState<string | null>(null);

  const refreshPrices = useCallback(async () => {
    setIsRefreshing(true);
    setPriceError(null);
    try {
      setAssets(await refreshMarketPrices());
    } catch (error) {
      setPriceError(error instanceof Error ? error.message : "Price refresh failed. Saved values are shown.");
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  const loadAssets = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);

    try {
      setAssets(await listAssets());
      void refreshPrices();
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "The collection could not be loaded.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [refreshPrices]);

  useEffect(() => {
    getHealth()
      .then(() => setApiState("online"))
      .catch(() => setApiState("offline"));

    void loadAssets();
  }, [loadAssets]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Pokémon Portfolio</p>
          <h1>Collection dashboard</h1>
          <p className="intro">
            Review every raw card, graded card, and sealed product in one place.
          </p>
        </div>
        <ApiStatus status={apiState} />
      </header>

      <div>
        <button className="secondary-button" onClick={() => void refreshPrices()} disabled={isRefreshing || isLoading}>
          {isRefreshing ? "Updating market prices..." : "Refresh market prices"}
        </button>
        {isRefreshing && <p role="status">Fetching card prices and updating market value, profit/loss and ROI. Saved values remain visible until complete.</p>}
        {priceError && <p role="alert">{priceError}</p>}
      </div>
      <CollectionDashboard
        assets={assets}
        initialFilter={preferences.defaultAssetTypeFilter}
        isLoading={isLoading}
        error={loadError}
        onRetry={() => void loadAssets()}
      />
      <PortfolioChatbot onPricingUpdated={setAssets} />
    </div>
  );
}
