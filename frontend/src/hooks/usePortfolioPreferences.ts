import { useContext } from "react";

import { PortfolioPreferencesContext } from "../preferences/PortfolioPreferencesContext";

export function usePortfolioPreferences() {
  const context = useContext(PortfolioPreferencesContext);

  if (context === null) {
    throw new Error(
      "usePortfolioPreferences must be used within PortfolioPreferencesProvider.",
    );
  }

  return context;
}
