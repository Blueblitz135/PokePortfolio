import { createContext } from "react";

import type { PortfolioPreferences } from "./portfolioPreferences";

export interface PortfolioPreferencesContextValue {
  preferences: PortfolioPreferences;
  storageAvailable: boolean;
  savePreferences: (preferences: PortfolioPreferences) => boolean;
  resetPreferences: () => boolean;
}

export const PortfolioPreferencesContext =
  createContext<PortfolioPreferencesContextValue | null>(null);
