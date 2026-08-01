import {
  DEFAULT_CURRENCY,
  type CurrencyCode,
} from "../types/currency";

export class UnsupportedCurrencyConversionError extends Error {
  constructor(fromCurrency: string, toCurrency: string) {
    super(`Conversion from ${fromCurrency} to ${toCurrency} is not supported.`);
    this.name = "UnsupportedCurrencyConversionError";
  }
}

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
