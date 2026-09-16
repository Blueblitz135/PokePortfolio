/** Validate ownership-specific fields used when adding a searched card. */
import type { CardAddDraft } from "../types/cardSearch";

/** Accept grades greater than zero through ten with at most one decimal place. */
function validateGrade(value: string): boolean {
  const normalizedValue = value.trim();
  if (!/^(?:\d{1,2}(?:\.\d)?|\.\d)$/.test(normalizedValue)) {
    return false;
  }

  const grade = Number(normalizedValue);
  return grade > 0 && grade <= 10;
}

/** Accept non-negative monetary input with at most two decimal places. */
function validatePurchasePrice(value: string): boolean {
  const normalizedValue = value.trim();
  return /^(?:\d{1,10}(?:\.\d{1,2})?|\.\d{1,2})$/.test(
    normalizedValue,
  );
}

/** Require a real ISO calendar date rather than relying on string shape alone. */
function validatePurchaseDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }

  const [year, month, day] = value.split("-").map(Number);
  const parsedDate = new Date(Date.UTC(year, month - 1, day));
  return (
    parsedDate.getUTCFullYear() === year &&
    parsedDate.getUTCMonth() === month - 1 &&
    parsedDate.getUTCDate() === day
  );
}

/** Return field-level errors for the optional initial purchase lot. */
export function validatePurchaseLotDraft(
  draft: CardAddDraft,
): string | null {
  if (!validatePurchaseDate(draft.purchaseDate)) {
    return "Enter a valid purchase date.";
  }

  if (
    !/^[1-9]\d*$/.test(draft.quantity) ||
    !Number.isSafeInteger(Number(draft.quantity))
  ) {
    return "Quantity must be a positive whole number.";
  }

  if (!validatePurchasePrice(draft.purchasePricePerUnit)) {
    return "Price must be zero or greater, with at most 10 whole-number digits and 2 decimal places.";
  }

  return null;
}

/** Validate common fields plus the selected raw or graded ownership details. */
export function validateCardAddDraft(
  draft: CardAddDraft,
): string | null {
  if (
    draft.assetType === "graded_card" &&
    !validateGrade(draft.grade)
  ) {
    return "Grade must be greater than 0, no greater than 10, and use at most one decimal place.";
  }

  if (
    draft.assetType === "graded_card" &&
    draft.certificationNumber.trim().length > 100
  ) {
    return "Certification number must be 100 characters or fewer.";
  }

  return validatePurchaseLotDraft(draft);
}
