/** Deterministic display-currency conversion helpers. */
import {
  DEFAULT_CURRENCY,
  type CurrencyCode,
} from "../types/currency";

export class UnsupportedCurrencyConversionError extends Error {
  /** Describe a requested conversion outside the supported rate table. */
  constructor(fromCurrency: string, toCurrency: string) {
    super(`Conversion from ${fromCurrency} to ${toCurrency} is not supported.`);
    this.name = "UnsupportedCurrencyConversionError";
  }
}

/** Convert through the fixed rate table; current MVP support is CAD-only. */
export function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string = DEFAULT_CURRENCY,
): { amount: number; currency: CurrencyCode } {
  if (fromCurrency === DEFAULT_CURRENCY && toCurrency === DEFAULT_CURRENCY) {
    return { amount, currency: DEFAULT_CURRENCY };
  }

  throw new UnsupportedCurrencyConversionError(fromCurrency, toCurrency);
}
