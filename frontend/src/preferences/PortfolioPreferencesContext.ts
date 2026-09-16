/** Context contract shared by the preferences provider and consumer hook. */
import { createContext } from "react";

import type { PortfolioPreferences } from "./portfolioPreferences";

/** Current preferences plus persistence-aware update operations. */
export interface PortfolioPreferencesContextValue {
  preferences: PortfolioPreferences;
  storageAvailable: boolean;
  savePreferences: (preferences: PortfolioPreferences) => boolean;
  resetPreferences: () => boolean;
}

/** Nullable default lets the consumer hook detect a missing provider. */
export const PortfolioPreferencesContext =
  createContext<PortfolioPreferencesContextValue | null>(null);
