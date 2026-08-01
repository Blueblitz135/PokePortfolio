import { useEffect, useState, type FormEvent } from "react";

import { usePortfolioPreferences } from "../hooks/usePortfolioPreferences";
import {
  DEFAULT_PORTFOLIO_PREFERENCES,
  PREFERENCES_VERSION,
  type PortfolioPreferences,
} from "../preferences/portfolioPreferences";

type Feedback = {
  kind: "success" | "error";
  message: string;
};

const COLLECTION_FILTER_OPTIONS: ReadonlyArray<{
  value: PortfolioPreferences["defaultAssetTypeFilter"];
  label: string;
}> = [
  { value: "all", label: "All assets" },
  { value: "raw_card", label: "Raw cards" },
  { value: "graded_card", label: "Graded cards" },
  { value: "sealed_product", label: "Sealed products" },
];

function copyPreferences(
  preferences: PortfolioPreferences,
): PortfolioPreferences {
  return {
    version: PREFERENCES_VERSION,
    displayCurrency: preferences.displayCurrency,
    defaultAssetTypeFilter: preferences.defaultAssetTypeFilter,
  };
}

export function SettingsPage() {
  const {
    preferences,
    storageAvailable,
    savePreferences,
    resetPreferences,
  } = usePortfolioPreferences();
  const [draft, setDraft] = useState<PortfolioPreferences>(() =>
    copyPreferences(preferences),
  );
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  useEffect(() => {
    setDraft(copyPreferences(preferences));
  }, [preferences]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const wasPersisted = savePreferences(copyPreferences(draft));
    setFeedback(
      wasPersisted
        ? {
            kind: "success",
            message: "Portfolio preferences saved in this browser.",
          }
        : {
            kind: "error",
            message:
              "Preferences are active for this session, but this browser could not save them.",
          },
    );
  }

  function handleReset() {
    const wasPersisted = resetPreferences();
    setDraft(copyPreferences(DEFAULT_PORTFOLIO_PREFERENCES));
    setFeedback(
      wasPersisted
        ? {
            kind: "success",
            message: "Portfolio preferences reset to the defaults.",
          }
        : {
            kind: "error",
            message:
              "Defaults are active for this session, but this browser could not save them.",
          },
    );
  }

  return (
    <div className="app-shell settings-page">
      <header className="app-header">
        <div>
          <p className="eyebrow">Settings</p>
          <h1>Portfolio preferences</h1>
          <p className="intro">
            Choose how this browser opens and displays your collection.
          </p>
        </div>
      </header>

      <section
        className="panel settings-panel"
        aria-labelledby="display-preferences-title"
      >
        <form className="settings-form" onSubmit={handleSubmit}>
          <div className="settings-section">
            <div>
              <h2 id="display-preferences-title">Display preferences</h2>
              <p className="settings-section-description">
                These choices affect presentation only. Stored portfolio values
                remain normalized in CAD.
              </p>
            </div>

            <label className="field" htmlFor="display-currency">
              <span>Display currency</span>
              <select
                id="display-currency"
                value={draft.displayCurrency}
                aria-describedby="display-currency-help"
                onChange={(event) => {
                  if (event.target.value === "CAD") {
                    setDraft((current) => ({
                      ...current,
                      displayCurrency: "CAD",
                    }));
                    setFeedback(null);
                  }
                }}
              >
                <option value="CAD">CAD - Canadian dollar</option>
                <option value="USD" disabled>
                  USD - Unavailable until currency conversion is added
                </option>
                <option value="EUR" disabled>
                  EUR - Unavailable until currency conversion is added
                </option>
                <option value="GBP" disabled>
                  GBP - Unavailable until currency conversion is added
                </option>
                <option value="JPY" disabled>
                  JPY - Unavailable until currency conversion is added
                </option>
              </select>
            </label>
            <p className="form-hint" id="display-currency-help">
              CAD is the only supported display currency. Other currencies
              cannot be selected until their numeric values can be converted;
              the app will never change only the currency symbol.
            </p>
          </div>

          <div className="settings-section">
            <div>
              <h2>Collection defaults</h2>
              <p className="settings-section-description">
                This filter is applied the next time you enter or refresh the
                Collection page. Filters you choose while browsing remain
                temporary.
              </p>
            </div>

            <label className="field" htmlFor="default-asset-type-filter">
              <span>Default collection filter</span>
              <select
                id="default-asset-type-filter"
                value={draft.defaultAssetTypeFilter}
                onChange={(event) => {
                  const selectedFilter = COLLECTION_FILTER_OPTIONS.find(
                    (option) => option.value === event.target.value,
                  );

                  if (selectedFilter) {
                    setDraft((current) => ({
                      ...current,
                      defaultAssetTypeFilter: selectedFilter.value,
                    }));
                    setFeedback(null);
                  }
                }}
              >
                {COLLECTION_FILTER_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <aside className="settings-storage-note" aria-label="Storage details">
            <h2>Stored in this browser only</h2>
            <p>
              These preferences are not an account and do not sync to other
              browsers or devices.
            </p>
          </aside>

          {!storageAvailable && (
            <p className="form-message form-message--error" role="alert">
              Browser storage is unavailable. You can use preferences during
              this session, but they may not survive a refresh.
            </p>
          )}

          {feedback && (
            <p
              className={`form-message form-message--${feedback.kind}`}
              role={feedback.kind === "error" ? "alert" : "status"}
            >
              {feedback.message}
            </p>
          )}

          <div className="settings-actions">
            <button className="primary-button" type="submit">
              Save preferences
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={handleReset}
            >
              Reset to defaults
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
