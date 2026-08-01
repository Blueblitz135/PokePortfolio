import {
  DEFAULT_CURRENCY,
  type CurrencyCode,
} from "../types/currency";

export const PREFERENCES_VERSION = 1 as const;
export const PORTFOLIO_PREFERENCES_STORAGE_KEY =
  "pokemonPortfolio.preferences.v1";

export const SUPPORTED_DEFAULT_ASSET_TYPE_FILTERS = [
  "all",
  "raw_card",
  "graded_card",
  "sealed_product",
] as const;

export type DefaultAssetTypeFilter =
  (typeof SUPPORTED_DEFAULT_ASSET_TYPE_FILTERS)[number];

export interface PortfolioPreferences {
  version: typeof PREFERENCES_VERSION;
  displayCurrency: CurrencyCode;
  defaultAssetTypeFilter: DefaultAssetTypeFilter;
}

export const DEFAULT_PORTFOLIO_PREFERENCES: PortfolioPreferences = {
  version: PREFERENCES_VERSION,
  displayCurrency: DEFAULT_CURRENCY,
  defaultAssetTypeFilter: "all",
};

export interface PortfolioPreferencesStorage {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

export interface PortfolioPreferencesReadResult {
  preferences: PortfolioPreferences;
  storageAvailable: boolean;
}

function defaultPreferences(): PortfolioPreferences {
  return { ...DEFAULT_PORTFOLIO_PREFERENCES };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isSupportedDisplayCurrency(value: unknown): value is CurrencyCode {
  return value === DEFAULT_CURRENCY;
}

function isSupportedDefaultAssetTypeFilter(
  value: unknown,
): value is DefaultAssetTypeFilter {
  return SUPPORTED_DEFAULT_ASSET_TYPE_FILTERS.some(
    (supportedFilter) => supportedFilter === value,
  );
}

export function parsePortfolioPreferences(value: unknown): PortfolioPreferences {
  if (!isRecord(value) || value.version !== PREFERENCES_VERSION) {
    return defaultPreferences();
  }

  return {
    version: PREFERENCES_VERSION,
    displayCurrency: isSupportedDisplayCurrency(value.displayCurrency)
      ? value.displayCurrency
      : DEFAULT_CURRENCY,
    defaultAssetTypeFilter: isSupportedDefaultAssetTypeFilter(
      value.defaultAssetTypeFilter,
    )
      ? value.defaultAssetTypeFilter
      : DEFAULT_PORTFOLIO_PREFERENCES.defaultAssetTypeFilter,
  };
}

export function deserializePortfolioPreferences(
  serializedPreferences: string | null,
): PortfolioPreferences {
  if (serializedPreferences === null) {
    return defaultPreferences();
  }

  try {
    return parsePortfolioPreferences(JSON.parse(serializedPreferences));
  } catch {
    return defaultPreferences();
  }
}

export function getPortfolioPreferencesStorage(): PortfolioPreferencesStorage | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function readPortfolioPreferences(
  storage: PortfolioPreferencesStorage | null =
    getPortfolioPreferencesStorage(),
): PortfolioPreferencesReadResult {
  if (storage === null) {
    return {
      preferences: defaultPreferences(),
      storageAvailable: false,
    };
  }

  try {
    return {
      preferences: deserializePortfolioPreferences(
        storage.getItem(PORTFOLIO_PREFERENCES_STORAGE_KEY),
      ),
      storageAvailable: true,
    };
  } catch {
    return {
      preferences: defaultPreferences(),
      storageAvailable: false,
    };
  }
}

export function writePortfolioPreferences(
  preferences: PortfolioPreferences,
  storage: PortfolioPreferencesStorage | null =
    getPortfolioPreferencesStorage(),
): boolean {
  if (storage === null) {
    return false;
  }

  const validatedPreferences = parsePortfolioPreferences(preferences);
  const storedPreferences: PortfolioPreferences = {
    version: PREFERENCES_VERSION,
    displayCurrency: validatedPreferences.displayCurrency,
    defaultAssetTypeFilter: validatedPreferences.defaultAssetTypeFilter,
  };

  try {
    storage.setItem(
      PORTFOLIO_PREFERENCES_STORAGE_KEY,
      JSON.stringify(storedPreferences),
    );
    return true;
  } catch {
    return false;
  }
}
