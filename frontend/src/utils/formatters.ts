import {
  DEFAULT_CURRENCY,
  type CurrencyCode,
} from "../types/currency";
import { convertCurrency } from "./currency";

export type CurrencyValue = string | number | null;

const currencyFormatters: Record<CurrencyCode, Intl.NumberFormat> = {
  CAD: new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
  }),
};

const percentFormatter = new Intl.NumberFormat("en-CA", {
  maximumFractionDigits: 1,
});

export function formatCurrency(
  value: CurrencyValue,
  currency: CurrencyCode = DEFAULT_CURRENCY,
): string {
  if (value === null) {
    return "—";
  }

  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "—";
  }

  return currencyFormatters[currency].format(amount);
}

export function formatCurrencyForDisplay(
  value: CurrencyValue,
  sourceCurrency: CurrencyCode,
  displayCurrency: CurrencyCode,
): string {
  if (value === null) {
    return "—";
  }

  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "—";
  }

  try {
    const converted = convertCurrency(
      amount,
      sourceCurrency,
      displayCurrency,
    );
    return formatCurrency(converted.amount, converted.currency);
  } catch {
    return formatCurrency(amount, sourceCurrency);
  }
}

export function formatPercent(value: string | null): string {
  if (value === null) {
    return "—";
  }

  const percentage = Number(value);
  return Number.isFinite(percentage)
    ? `${percentFormatter.format(percentage)}%`
    : "—";
}
