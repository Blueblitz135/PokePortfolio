import { useCallback } from "react";

import type { CurrencyCode } from "../types/currency";
import {
  formatCurrencyForDisplay,
  type CurrencyValue,
} from "../utils/formatters";
import { usePortfolioPreferences } from "./usePortfolioPreferences";

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
