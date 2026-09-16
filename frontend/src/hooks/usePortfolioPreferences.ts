/** Safe consumer hook for the portfolio-preferences context. */
import { useContext } from "react";

import { PortfolioPreferencesContext } from "../preferences/PortfolioPreferencesContext";

/** Return preference state and fail clearly when no provider is mounted. */
export function usePortfolioPreferences() {
  const context = useContext(PortfolioPreferencesContext);

  if (context === null) {
    throw new Error(
      "usePortfolioPreferences must be used within PortfolioPreferencesProvider.",
    );
  }

  return context;
}
