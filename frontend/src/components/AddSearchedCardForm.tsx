import { type FormEvent, useState } from "react";

import type {
  GradingCompany,
  RawCardCondition,
} from "../types/assets";
import type {
  CardAddDraft,
  CardOwnershipType,
  CardSearchResult,
} from "../types/cardSearch";
import { formatSearchCardNumber } from "../types/cardSearch";
import { validateCardAddDraft } from "../utils/cardAddValidation";

const RAW_CONDITIONS: ReadonlyArray<{
  value: RawCardCondition;
  label: string;
}> = [
  { value: "NM", label: "Near Mint (NM)" },
  { value: "LP", label: "Lightly Played (LP)" },
  { value: "MP", label: "Moderately Played (MP)" },
  { value: "DMG", label: "Damaged (DMG)" },
];

const GRADING_COMPANIES: ReadonlyArray<GradingCompany> = [
  "PSA",
  "BGS",
  "CGC",
  "TAG",
  "OTHER",
];

function getToday(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function createDefaultDraft(): CardAddDraft {
  return {
    assetType: "raw_card",
    rawCondition: "NM",
    gradingCompany: "PSA",
    grade: "10",
    certificationNumber: "",
    userNote: "",
    purchaseDate: getToday(),
    quantity: "1",
    purchasePricePerUnit: "",
  };
}

interface AddSearchedCardFormProps {
  card: CardSearchResult;
  initialDraft: CardAddDraft | null;
  onReview: (draft: CardAddDraft) => void;
  onCancel: () => void;
}

export function AddSearchedCardForm({
  card,
  initialDraft,
  onReview,
  onCancel,
}: AddSearchedCardFormProps) {
  const [draft, setDraft] = useState<CardAddDraft>(
    () => initialDraft ?? createDefaultDraft(),
  );
  const [error, setError] = useState<string | null>(null);

  function updateDraft<K extends keyof CardAddDraft>(
    field: K,
    value: CardAddDraft[K],
  ) {
    setDraft((current) => ({ ...current, [field]: value }));
    setError(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validateCardAddDraft(draft);

    if (validationError) {
      setError(validationError);
      return;
    }

    onReview({
      ...draft,
      grade: draft.grade.trim(),
      certificationNumber: draft.certificationNumber.trim(),
      userNote: draft.userNote.trim(),
      quantity: draft.quantity.trim(),
      purchasePricePerUnit: draft.purchasePricePerUnit.trim(),
    });
  }

  return (
    <section
      className="panel searched-card-form-panel"
      id="ownership-details"
      aria-labelledby="ownership-title"
    >
      <div className="selected-search-card">
        <div>
          <p className="eyebrow">Selected card</p>
          <h2 id="ownership-title" tabIndex={-1}>
            {card.name}
          </h2>
          <p>
            {card.set_name} · {formatSearchCardNumber(card)}
          </p>
        </div>
        <button className="secondary-button" type="button" onClick={onCancel}>
          Choose another card
        </button>
      </div>

      <form className="searched-card-form" onSubmit={handleSubmit} noValidate>
        <fieldset className="ownership-type-fieldset">
          <legend>How is your copy owned?</legend>
          <div className="ownership-type-options">
            {(
              [
                ["raw_card", "Raw card"],
                ["graded_card", "Graded card"],
              ] satisfies ReadonlyArray<[CardOwnershipType, string]>
            ).map(([value, label]) => (
              <label
                className={`ownership-type-option ${
                  draft.assetType === value
                    ? "ownership-type-option--selected"
                    : ""
                }`}
                key={value}
              >
                <input
                  type="radio"
                  name="asset-type"
                  value={value}
                  checked={draft.assetType === value}
                  onChange={() => updateDraft("assetType", value)}
                />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <div className="form-grid">
          {draft.assetType === "raw_card" ? (
            <label className="field field--wide">
              <span>Condition</span>
              <select
                value={draft.rawCondition}
                onChange={(event) =>
                  updateDraft(
                    "rawCondition",
                    event.target.value as RawCardCondition,
                  )
                }
              >
                {RAW_CONDITIONS.map((condition) => (
                  <option key={condition.value} value={condition.value}>
                    {condition.label}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <>
              <label className="field">
                <span>Grading company</span>
                <select
                  value={draft.gradingCompany}
                  onChange={(event) =>
                    updateDraft(
                      "gradingCompany",
                      event.target.value as GradingCompany,
                    )
                  }
                >
                  {GRADING_COMPANIES.map((company) => (
                    <option key={company} value={company}>
                      {company}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Grade</span>
                <input
                  required
                  type="text"
                  inputMode="decimal"
                  value={draft.grade}
                  aria-describedby="grade-hint"
                  onChange={(event) =>
                    updateDraft("grade", event.target.value)
                  }
                  placeholder="10"
                />
                <small className="form-hint" id="grade-hint">
                  Greater than 0 and no higher than 10; one decimal maximum.
                </small>
              </label>

              <label className="field field--wide">
                <span>Certification number</span>
                <input
                  type="text"
                  maxLength={100}
                  value={draft.certificationNumber}
                  onChange={(event) =>
                    updateDraft(
                      "certificationNumber",
                      event.target.value,
                    )
                  }
                  placeholder="Optional"
                />
              </label>
            </>
          )}

          <label className="field field--wide">
            <span>Overall note</span>
            <textarea
              rows={3}
              value={draft.userNote}
              onChange={(event) =>
                updateDraft("userNote", event.target.value)
              }
              placeholder="Optional note about your copy"
            />
          </label>
        </div>

        <fieldset className="purchase-details-fieldset">
          <legend>First purchase lot</legend>
          <div className="form-grid form-grid--compact">
            <label className="field">
              <span>Purchase date</span>
              <input
                required
                type="date"
                value={draft.purchaseDate}
                onChange={(event) =>
                  updateDraft("purchaseDate", event.target.value)
                }
              />
            </label>

            <label className="field">
              <span>Quantity</span>
              <input
                required
                type="text"
                inputMode="numeric"
                value={draft.quantity}
                onChange={(event) =>
                  updateDraft("quantity", event.target.value)
                }
                placeholder="1"
              />
            </label>

            <label className="field">
              <span>Price per unit (CAD)</span>
              <input
                required
                type="text"
                inputMode="decimal"
                value={draft.purchasePricePerUnit}
                onChange={(event) =>
                  updateDraft(
                    "purchasePricePerUnit",
                    event.target.value,
                  )
                }
                placeholder="25.00"
              />
            </label>
          </div>
        </fieldset>

        {error && (
          <p className="form-message form-message--error" role="alert">
            {error}
          </p>
        )}

        <div className="search-form-actions">
          <button className="primary-button" type="submit">
            Review card and purchase
          </button>
          <button className="secondary-button" type="button" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
