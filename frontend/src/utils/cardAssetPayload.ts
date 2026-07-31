import type {
  CardAssetCreatePayload,
  PurchaseLotCreatePayload,
} from "../types/assets";
import type {
  CardAddDraft,
  CardSearchResult,
} from "../types/cardSearch";

function normalizeLeadingDecimal(value: string): string {
  const trimmedValue = value.trim();
  return trimmedValue.startsWith(".") ? `0${trimmedValue}` : trimmedValue;
}

export function buildCardAssetPayload(
  card: CardSearchResult,
  draft: CardAddDraft,
): CardAssetCreatePayload {
  const cardMetadata = {
    external_source: card.external_source,
    external_id: card.external_id,
    name: card.name,
    set_name: card.set_name,
    set_id: card.set_id,
    year: card.year,
    card_number: card.card_number,
    set_total: card.set_total,
    rarity: card.rarity,
    variant: null,
    image_url: card.image_url,
  };
  const userNote = draft.userNote.trim() || null;

  if (draft.assetType === "raw_card") {
    return {
      asset_type: "raw_card",
      display_name: card.name,
      user_note: userNote,
      card_metadata: cardMetadata,
      raw_details: {
        condition: draft.rawCondition,
      },
    };
  }

  return {
    asset_type: "graded_card",
    display_name: card.name,
    user_note: userNote,
    card_metadata: cardMetadata,
    graded_details: {
      grading_company: draft.gradingCompany,
      grade: normalizeLeadingDecimal(draft.grade),
      cert_number: draft.certificationNumber.trim() || null,
    },
  };
}

export function buildFirstPurchaseLotPayload(
  draft: CardAddDraft,
): PurchaseLotCreatePayload {
  return {
    purchase_date: draft.purchaseDate,
    quantity: Number(draft.quantity),
    purchase_price_per_unit: normalizeLeadingDecimal(
      draft.purchasePricePerUnit,
    ),
    currency: "CAD",
  };
}
