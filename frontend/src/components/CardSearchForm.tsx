import type { FormEvent } from "react";

interface CardSearchFormProps {
  query: string;
  validationError: string | null;
  isSearching: boolean;
  disabled: boolean;
  onQueryChange: (query: string) => void;
  onSearch: () => void;
}

export function CardSearchForm({
  query,
  validationError,
  isSearching,
  disabled,
  onQueryChange,
  onSearch,
}: CardSearchFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className="card-search-form" onSubmit={handleSubmit} noValidate>
      <label className="field" htmlFor="card-search-query">
        <span>Card name, set, or number</span>
        <input
          id="card-search-query"
          type="search"
          value={query}
          disabled={disabled}
          aria-describedby="card-search-hint"
          aria-invalid={validationError ? "true" : undefined}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Umbreon VMAX Evolving Skies"
        />
      </label>
      <button className="primary-button" type="submit" disabled={disabled}>
        Search cards
      </button>
      <p className="form-hint" id="card-search-hint">
        Enter between 1 and 100 characters. Search covers individual cards,
        not sealed products.
      </p>
      {validationError && (
        <p className="form-message form-message--error" role="alert">
          {validationError}
        </p>
      )}
      {isSearching && (
        <p className="search-inline-status" role="status">
          Searching TCGdex...
        </p>
      )}
    </form>
  );
}
