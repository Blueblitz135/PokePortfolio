/** Types and identity helpers for the TCGdex search-to-collection workflow. */
import type {
  AssetType,
  ExternalSource,
  GradingCompany,
  RawCardCondition,
} from "./assets";

/** Provider-independent card metadata returned by the backend search endpoint. */
export interface CardSearchResult {
  external_source: ExternalSource;
  external_id: string;
  name: string;
  set_name: string;
  set_id: string;
  year: number | null;
  card_number: string;
  set_total: string | null;
  rarity: string | null;
  image_url: string | null;
}

export type CardOwnershipType = Extract<
  AssetType,
  "raw_card" | "graded_card"
>;

/** User-entered ownership details collected after selecting a search result. */
export interface CardAddDraft {
  assetType: CardOwnershipType;
  rawCondition: RawCardCondition;
  gradingCompany: GradingCompany;
  grade: string;
  certificationNumber: string;
  userNote: string;
  purchaseDate: string;
  quantity: string;
  purchasePricePerUnit: string;
}

/** Recoverable failure attached to one phase of the two-request save workflow. */
export interface CardSaveIssue {
  kind:
    | "definite"
    | "ambiguous"
    | "partial_definite"
    | "partial_ambiguous";
  message: string;
}

export type CardSavePhase =
  | "idle"
  | "creating_asset"
  | "creating_lot"
  | "partial"
  | "complete";

/** Build a stable selection key from provider and provider identifier. */
export function getCardSearchResultKey(result: CardSearchResult): string {
  return `${result.external_source}:${result.external_id}`;
}

/** Display the structured card number with its optional set total. */
export function formatSearchCardNumber(result: CardSearchResult): string {
  return result.set_total
    ? `${result.card_number}/${result.set_total}`
    : result.card_number;
}
