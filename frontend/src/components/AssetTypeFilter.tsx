import type { DefaultAssetTypeFilter } from "../preferences/portfolioPreferences";

export type AssetFilter = DefaultAssetTypeFilter;

interface AssetTypeFilterProps {
  selectedFilter: AssetFilter;
  counts: Record<AssetFilter, number>;
  onChange: (filter: AssetFilter) => void;
}

const FILTER_OPTIONS: ReadonlyArray<{
  value: AssetFilter;
  label: string;
}> = [
  { value: "all", label: "All" },
  { value: "raw_card", label: "Raw cards" },
  { value: "graded_card", label: "Graded cards" },
  { value: "sealed_product", label: "Sealed products" },
];

export function AssetTypeFilter({
  selectedFilter,
  counts,
  onChange,
}: AssetTypeFilterProps) {
  return (
    <fieldset className="asset-filters">
      <legend>Filter collection by asset type</legend>
      <div className="filter-options">
        {FILTER_OPTIONS.map((option) => (
          <button
            className="filter-button"
            type="button"
            key={option.value}
            aria-pressed={selectedFilter === option.value}
            onClick={() => onChange(option.value)}
          >
            <span>{option.label}</span>
            <span className="filter-count">{counts[option.value]}</span>
          </button>
        ))}
      </div>
    </fieldset>
  );
}
