import { describe, expect, it } from "vitest";

import {
  DEFAULT_PORTFOLIO_PREFERENCES,
  deserializePortfolioPreferences,
  PORTFOLIO_PREFERENCES_STORAGE_KEY,
  readPortfolioPreferences,
  writePortfolioPreferences,
  type PortfolioPreferencesStorage,
} from "./portfolioPreferences";

function createStorage(): PortfolioPreferencesStorage & { value: string | null } {
  return {
    value: null,
    getItem() {
      return this.value;
    },
    setItem(key, value) {
      expect(key).toBe(PORTFOLIO_PREFERENCES_STORAGE_KEY);
      this.value = value;
    },
  };
}

describe("portfolio preferences", () => {
  it("uses defaults for malformed or future-version stored data", () => {
    expect(deserializePortfolioPreferences("not valid json")).toEqual(
      DEFAULT_PORTFOLIO_PREFERENCES,
    );
    expect(
      deserializePortfolioPreferences(
        JSON.stringify({
          version: 2,
          displayCurrency: "CAD",
          defaultAssetTypeFilter: "raw_card",
        }),
      ),
    ).toEqual(DEFAULT_PORTFOLIO_PREFERENCES);
  });

  it("normalizes unsupported fields without discarding valid version-one fields", () => {
    expect(
      deserializePortfolioPreferences(
        JSON.stringify({
          version: 1,
          displayCurrency: "USD",
          defaultAssetTypeFilter: "graded_card",
        }),
      ),
    ).toEqual({
      version: 1,
      displayCurrency: "CAD",
      defaultAssetTypeFilter: "graded_card",
    });
  });

  it("writes only the supported versioned fields", () => {
    const storage = createStorage();

    expect(
      writePortfolioPreferences(
        {
          version: 1,
          displayCurrency: "CAD",
          defaultAssetTypeFilter: "sealed_product",
        },
        storage,
      ),
    ).toBe(true);
    expect(JSON.parse(storage.value ?? "")).toEqual({
      version: 1,
      displayCurrency: "CAD",
      defaultAssetTypeFilter: "sealed_product",
    });
  });

  it("falls back safely when browser storage throws", () => {
    const failingStorage: PortfolioPreferencesStorage = {
      getItem() {
        throw new Error("storage is unavailable");
      },
      setItem() {
        throw new Error("storage is unavailable");
      },
    };

    expect(readPortfolioPreferences(failingStorage)).toEqual({
      preferences: DEFAULT_PORTFOLIO_PREFERENCES,
      storageAvailable: false,
    });
    expect(
      writePortfolioPreferences(DEFAULT_PORTFOLIO_PREFERENCES, failingStorage),
    ).toBe(false);
  });
});
