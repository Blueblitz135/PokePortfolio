import { describe, expect, it } from "vitest";

import type { CurrencyCode } from "../types/currency";
import { formatCurrency, formatCurrencyForDisplay } from "./formatters";

describe("currency formatting", () => {
  it("formats CAD values through the identity conversion path", () => {
    expect(formatCurrencyForDisplay("12.34", "CAD", "CAD")).toBe(
      formatCurrency("12.34", "CAD"),
    );
  });

  it("keeps the source CAD label when a requested conversion is unsupported", () => {
    const unsupportedCurrency = "USD" as unknown as CurrencyCode;

    expect(
      formatCurrencyForDisplay("12.34", "CAD", unsupportedCurrency),
    ).toBe(formatCurrency("12.34", "CAD"));
  });
});
