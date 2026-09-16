/** Bind currency formatting to the user's current portfolio preferences. */
import { useCallback } from "react";

import type { CurrencyCode } from "../types/currency";
import {
  formatCurrencyForDisplay,
  type CurrencyValue,
} from "../utils/formatters";
import { usePortfolioPreferences } from "./usePortfolioPreferences";

/** Return a stable formatter and selected display currency. */
export function useCurrencyFormatter() {
  const { preferences } = usePortfolioPreferences();

  return useCallback(
    (value: CurrencyValue, sourceCurrency: CurrencyCode) =>
      formatCurrencyForDisplay(
        value,
        sourceCurrency,
        preferences.displayCurrency,
      ),
    [preferences.displayCurrency],
  );
}
