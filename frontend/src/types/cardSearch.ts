import type {
  AssetType,
  ExternalSource,
  GradingCompany,
  RawCardCondition,
} from "./assets";

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

export function getCardSearchResultKey(result: CardSearchResult): string {
  return `${result.external_source}:${result.external_id}`;
}

export function formatSearchCardNumber(result: CardSearchResult): string {
  return result.set_total
    ? `${result.card_number}/${result.set_total}`
    : result.card_number;
}
