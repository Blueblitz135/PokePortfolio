import { useCallback, useEffect, useState } from "react";

import { listAssets } from "../api/assets";
import { getHealth } from "../api/health";
import { ApiStatus } from "../components/ApiStatus";
import { CollectionDashboard } from "../components/CollectionDashboard";
import type { AssetResponse } from "../types/assets";

type ApiState = "loading" | "online" | "offline";

export function CollectionPage() {
  const [apiState, setApiState] = useState<ApiState>("loading");
  const [assets, setAssets] = useState<AssetResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadAssets = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);

    try {
      setAssets(await listAssets());
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "The collection could not be loaded.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    getHealth()
      .then(() => setApiState("online"))
      .catch(() => setApiState("offline"));

    void loadAssets();
  }, [loadAssets]);

  return (
    <main className="app-shell">
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

      <CollectionDashboard
        assets={assets}
        isLoading={isLoading}
        error={loadError}
        onRetry={() => void loadAssets()}
      />
    </main>
  );
}
