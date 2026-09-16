/** Review and submit the selected card plus optional first purchase lot. */
import { type FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useCurrencyFormatter } from "../hooks/useCurrencyFormatter";
import type {
  CardAddDraft,
  CardSaveIssue,
  CardSavePhase,
  CardSearchResult,
} from "../types/cardSearch";
import { formatSearchCardNumber } from "../types/cardSearch";
import { validatePurchaseLotDraft } from "../utils/cardAddValidation";

interface CardAddConfirmationProps {
  card: CardSearchResult;
  draft: CardAddDraft;
  savePhase: CardSavePhase;
  saveIssue: CardSaveIssue | null;
  createdAssetId: number | null;
  ambiguousRetryConfirmed: boolean;
  onBack: () => void;
  onConfirm: () => void;
  onRetryLot: (updatedDraft: CardAddDraft) => void;
  onStartOver: () => void;
  onAmbiguousRetryChange: (confirmed: boolean) => void;
}

/** Summarize condition or grading details for the confirmation view. */
function ownershipDescription(draft: CardAddDraft): string {
  if (draft.assetType === "raw_card") {
    return `Raw card · ${draft.rawCondition}`;
  }

  return `Graded card · ${draft.gradingCompany} ${draft.grade}`;
}

/** Confirm the two-step save and expose targeted recovery actions on failure. */
export function CardAddConfirmation({
  card,
  draft,
  savePhase,
  saveIssue,
  createdAssetId,
  ambiguousRetryConfirmed,
  onBack,
  onConfirm,
  onRetryLot,
  onStartOver,
  onAmbiguousRetryChange,
}: CardAddConfirmationProps) {
  const formatCurrency = useCurrencyFormatter();
  const [recoveryDraft, setRecoveryDraft] = useState(draft);
  const [recoveryError, setRecoveryError] = useState<string | null>(null);
  const [hasCheckedPurchaseLots, setHasCheckedPurchaseLots] =
    useState(false);
  const isSaving =
    savePhase === "creating_asset" || savePhase === "creating_lot";

  useEffect(() => {
    if (savePhase === "complete" || savePhase === "partial") {
      window.requestAnimationFrame(() => {
        document.getElementById("card-add-outcome-title")?.focus();
      });
    }
  }, [savePhase]);

  /** Update fields shown when retrying a failed initial purchase lot. */
  function updateRecoveryDraft(
    field: "purchaseDate" | "quantity" | "purchasePricePerUnit",
    value: string,
  ) {
    setRecoveryDraft((current) => ({ ...current, [field]: value }));
    setRecoveryError(null);
  }

  /** Validate revised lot data before asking the parent to retry only that step. */
  function handleRecoverySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validatePurchaseLotDraft(recoveryDraft);
    if (validationError) {
      setRecoveryError(validationError);
      return;
    }

    if (
      saveIssue?.kind === "partial_ambiguous" &&
      !hasCheckedPurchaseLots
    ) {
      setRecoveryError(
        "Inspect the asset and confirm the purchase lot is missing before retrying.",
      );
      return;
    }

    setRecoveryError(null);
    setHasCheckedPurchaseLots(false);
    onRetryLot({
      ...recoveryDraft,
      quantity: recoveryDraft.quantity.trim(),
      purchasePricePerUnit:
        recoveryDraft.purchasePricePerUnit.trim(),
    });
  }

  if (savePhase === "complete" && createdAssetId !== null) {
    return (
      <section
        className="panel card-add-outcome card-add-outcome--success"
        role="status"
      >
        <p className="eyebrow">Added to collection</p>
        <h2 id="card-add-outcome-title" tabIndex={-1}>
          {card.name} is ready
        </h2>
        <p>
          The card and its first purchase lot were created successfully.
        </p>
        <div className="search-form-actions">
          <Link
            className="primary-button button-link"
            to={`/assets/${createdAssetId}`}
          >
            Open asset details
          </Link>
          <Link className="secondary-button button-link" to="/collection">
            Return to collection
          </Link>
          <button
            className="secondary-button"
            type="button"
            onClick={onStartOver}
          >
            Search for another card
          </button>
        </div>
      </section>
    );
  }

  if (savePhase === "creating_lot" && createdAssetId !== null) {
    return (
      <section className="panel card-add-outcome" role="status">
        <p className="eyebrow">Card created</p>
        <h2>Adding the first purchase lot...</h2>
        <p>
          The asset now exists. The purchase record is being saved to that
          asset.
        </p>
      </section>
    );
  }

  if (savePhase === "partial" && createdAssetId !== null) {
    return (
      <section className="panel card-add-outcome card-add-outcome--partial">
        <p className="eyebrow">Purchase record needs attention</p>
        <h2 id="card-add-outcome-title" tabIndex={-1}>
          The card was added
        </h2>
        <p role="alert">{saveIssue?.message}</p>
        <p>
          Correct the purchase details if needed. Saving here sends only the
          purchase lot and will not create the card again.
        </p>

        <form
          className="partial-lot-recovery"
          onSubmit={handleRecoverySubmit}
          noValidate
        >
          <div className="form-grid form-grid--compact">
            <label className="field">
              <span>Purchase date</span>
              <input
                type="date"
                value={recoveryDraft.purchaseDate}
                onChange={(event) =>
                  updateRecoveryDraft(
                    "purchaseDate",
                    event.target.value,
                  )
                }
              />
            </label>
            <label className="field">
              <span>Quantity</span>
              <input
                type="text"
                inputMode="numeric"
                value={recoveryDraft.quantity}
                onChange={(event) =>
                  updateRecoveryDraft("quantity", event.target.value)
                }
              />
            </label>
            <label className="field">
              <span>Price per unit (CAD)</span>
              <input
                type="text"
                inputMode="decimal"
                value={recoveryDraft.purchasePricePerUnit}
                onChange={(event) =>
                  updateRecoveryDraft(
                    "purchasePricePerUnit",
                    event.target.value,
                  )
                }
              />
            </label>
          </div>

          {saveIssue?.kind === "partial_ambiguous" && (
            <label className="checkbox-field partial-retry-check">
              <input
                type="checkbox"
                checked={hasCheckedPurchaseLots}
                onChange={(event) =>
                  setHasCheckedPurchaseLots(event.target.checked)
                }
              />
              <span>
                I inspected the asset and confirmed this purchase lot is
                missing.
              </span>
            </label>
          )}

          {recoveryError && (
            <p className="form-message form-message--error" role="alert">
              {recoveryError}
            </p>
          )}

          <button className="primary-button" type="submit">
            Save purchase lot
          </button>
        </form>

        <div className="search-form-actions">
          <Link
            className="secondary-button button-link"
            to={`/assets/${createdAssetId}`}
            target="_blank"
            rel="noreferrer"
          >
            Inspect asset in a new tab
          </Link>
          <Link className="secondary-button button-link" to="/collection">
            Return to collection
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section
      className="panel card-add-confirmation"
      aria-labelledby="confirmation-title"
      aria-busy={isSaving}
    >
      <div>
        <p className="eyebrow">Final confirmation</p>
        <h2 id="confirmation-title" tabIndex={-1}>
          Add {card.name}?
        </h2>
        <p className="confirmation-intro">
          Confirm the card identity and ownership details. Nothing is created
          until you use the confirmation button.
        </p>
      </div>

      <dl className="confirmation-grid">
        <div>
          <dt>Card</dt>
          <dd>{card.name}</dd>
        </div>
        <div>
          <dt>Set</dt>
          <dd>{card.set_name}</dd>
        </div>
        <div>
          <dt>Card number</dt>
          <dd>{formatSearchCardNumber(card)}</dd>
        </div>
        <div>
          <dt>Ownership</dt>
          <dd>{ownershipDescription(draft)}</dd>
        </div>
        {draft.assetType === "graded_card" &&
          draft.certificationNumber && (
            <div>
              <dt>Certification</dt>
              <dd>{draft.certificationNumber}</dd>
            </div>
          )}
        <div>
          <dt>Purchase date</dt>
          <dd>{draft.purchaseDate}</dd>
        </div>
        <div>
          <dt>Quantity</dt>
          <dd>{draft.quantity}</dd>
        </div>
        <div>
          <dt>Price per unit</dt>
          <dd>{formatCurrency(draft.purchasePricePerUnit, "CAD")}</dd>
        </div>
        <div>
          <dt>Currency</dt>
          <dd>CAD</dd>
        </div>
        {draft.userNote && (
          <div className="confirmation-note">
            <dt>Note</dt>
            <dd>{draft.userNote}</dd>
          </div>
        )}
      </dl>

      {saveIssue && (
        <div className="form-message form-message--error" role="alert">
          <p>{saveIssue.message}</p>
          {saveIssue.kind === "ambiguous" && (
            <Link to="/collection">Check Collection before trying again.</Link>
          )}
        </div>
      )}

      {saveIssue?.kind === "ambiguous" && (
        <label className="checkbox-field ambiguous-retry-check">
          <input
            type="checkbox"
            checked={ambiguousRetryConfirmed}
            onChange={(event) =>
              onAmbiguousRetryChange(event.target.checked)
            }
          />
          <span>
            I checked Collection and confirmed this card was not added.
          </span>
        </label>
      )}

      {isSaving && (
        <p className="form-message form-message--success" role="status">
          {savePhase === "creating_asset"
            ? "Creating the card asset..."
            : "Card created. Adding the first purchase lot..."}
        </p>
      )}

      <div className="search-form-actions">
        <button
          className="primary-button"
          type="button"
          disabled={
            isSaving ||
            (saveIssue?.kind === "ambiguous" &&
              !ambiguousRetryConfirmed)
          }
          onClick={onConfirm}
        >
          {isSaving ? "Saving..." : "Confirm and add to collection"}
        </button>
        <button
          className="secondary-button"
          type="button"
          disabled={isSaving}
          onClick={onBack}
        >
          Back to edit
        </button>
      </div>
    </section>
  );
}
