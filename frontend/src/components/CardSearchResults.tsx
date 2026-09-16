/** Present normalized TCGdex results and allow one card to be selected. */
import type { CardSearchResult } from "../types/cardSearch";
import {
  formatSearchCardNumber,
  getCardSearchResultKey,
} from "../types/cardSearch";

const PLACEHOLDER_IMAGE_URL = "/static/placeholders/asset.svg";

interface CardSearchResultsProps {
  results: CardSearchResult[];
  submittedQuery: string;
  hasSearched: boolean;
  isLoading: boolean;
  error: string | null;
  selectedCard: CardSearchResult | null;
  disabled: boolean;
  onSelect: (card: CardSearchResult) => void;
  onRetry: () => void;
}

/** Build a compact list of optional set, year, rarity, and number details. */
function resultDetails(result: CardSearchResult): string[] {
  return [
    result.set_name,
    formatSearchCardNumber(result),
    result.rarity,
    result.year?.toString(),
  ].filter((value): value is string => Boolean(value));
}

/** Render initial, empty, error, loading, or selectable result states. */
export function CardSearchResults({
  results,
  submittedQuery,
  hasSearched,
  isLoading,
  error,
  selectedCard,
  disabled,
  onSelect,
  onRetry,
}: CardSearchResultsProps) {
  if (isLoading) {
    return (
      <section className="panel search-state-panel" aria-live="polite">
        <h2>Searching cards</h2>
        <p>Looking for “{submittedQuery}”...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel search-state-panel" role="alert">
        <h2>Card search unavailable</h2>
        <p>{error}</p>
        <button className="secondary-button" type="button" onClick={onRetry}>
          Try this search again
        </button>
      </section>
    );
  }

  if (!hasSearched) {
    return (
      <section className="panel search-state-panel">
        <h2>Search for a card</h2>
        <p>
          Results will show normalized card identity from TCGdex. Selecting a
          result does not add it to your collection.
        </p>
      </section>
    );
  }

  if (results.length === 0) {
    return (
      <section className="panel search-state-panel" role="status">
        <h2>No cards found</h2>
        <p>
          No results matched “{submittedQuery}”. Try a shorter card name or
          remove extra set details.
        </p>
      </section>
    );
  }

  const selectedKey = selectedCard
    ? getCardSearchResultKey(selectedCard)
    : null;

  return (
    <section className="search-results-section" aria-labelledby="results-title">
      <p className="visually-hidden" role="status">
        {results.length} {results.length === 1 ? "card" : "cards"} found for{" "}
        {submittedQuery}.
      </p>
      <div className="search-section-heading">
        <div>
          <p className="eyebrow">TCGdex results</p>
          <h2 id="results-title">
            {results.length} {results.length === 1 ? "card" : "cards"} found
          </h2>
        </div>
        <p>Select the exact printing you own.</p>
      </div>

      <ul className="card-search-results">
        {results.map((result) => {
          const resultKey = getCardSearchResultKey(result);
          const isSelected = resultKey === selectedKey;

          return (
            <li key={resultKey}>
              <button
                className={`card-search-result ${
                  isSelected ? "card-search-result--selected" : ""
                }`}
                type="button"
                disabled={disabled}
                aria-pressed={isSelected}
                onClick={() => onSelect(result)}
              >
                <img
                  src={result.image_url ?? PLACEHOLDER_IMAGE_URL}
                  alt={`${result.name} card`}
                  loading="lazy"
                  onError={(event) => {
                    event.currentTarget.onerror = null;
                    event.currentTarget.src = PLACEHOLDER_IMAGE_URL;
                  }}
                />
                <span className="card-search-result-copy">
                  <strong>{result.name}</strong>
                  <span>{resultDetails(result).join(" · ")}</span>
                  <span className="card-search-result-action">
                    {isSelected ? "Selected" : "Select card"}
                  </span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
