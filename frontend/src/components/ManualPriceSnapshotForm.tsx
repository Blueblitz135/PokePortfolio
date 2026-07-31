import { type FormEvent, useRef, useState } from "react";

import { createManualPriceSnapshot } from "../api/assets";
import type { PriceSnapshot } from "../types/assets";
import { formatCurrency } from "../utils/formatters";

interface ManualPriceSnapshotFormProps {
  assetId: number;
  latestSnapshot: PriceSnapshot | null;
  onSaved: () => Promise<void>;
}

const cadAmountPattern = /^(?:\d{1,10}(?:\.\d{1,2})?|\.\d{1,2})$/;

function validatePrice(value: string): string | null {
  if (!cadAmountPattern.test(value.trim())) {
    return "Enter a price from 0 to 9,999,999,999.99 with no more than 2 decimal places.";
  }

  return null;
}

function formatObservedAt(value: string): string {
  const hasTimeZone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value);
  const observedAt = new Date(hasTimeZone ? value : `${value}Z`);

  if (Number.isNaN(observedAt.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-CA", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(observedAt);
}

function formatConfidence(value: string | null): string {
  if (value === null) {
    return "Not available";
  }

  const confidence = Number(value);

  return Number.isFinite(confidence)
    ? `${Math.round(confidence * 100)}%`
    : "Not available";
}

export function ManualPriceSnapshotForm({
  assetId,
  latestSnapshot,
  onSaved,
}: ManualPriceSnapshotFormProps) {
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [needsRefresh, setNeedsRefresh] = useState(false);
  const submissionInProgress = useRef(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (submissionInProgress.current) {
      return;
    }

    const normalizedPrice = pricePerUnit.trim();
    const validationError = validatePrice(normalizedPrice);
    if (validationError !== null) {
      setError(validationError);
      setSuccess(null);
      return;
    }

    submissionInProgress.current = true;
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);
    setNeedsRefresh(false);

    try {
      await createManualPriceSnapshot(assetId, {
        market_price_per_unit: normalizedPrice,
        currency: "CAD",
        source: "manual",
        confidence: 0.5,
      });
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "The manual price snapshot could not be saved.",
      );
      submissionInProgress.current = false;
      setIsSubmitting(false);
      return;
    }

    setPricePerUnit("");

    try {
      await onSaved();
      setSuccess("Manual price saved and portfolio calculations updated.");
    } catch {
      setError(
        "The manual price was saved, but the asset summary could not be refreshed. Retry the refresh to see the updated calculations.",
      );
      setNeedsRefresh(true);
    } finally {
      submissionInProgress.current = false;
      setIsSubmitting(false);
    }
  }

  async function handleRetryRefresh() {
    if (submissionInProgress.current) {
      return;
    }

    submissionInProgress.current = true;
    setIsSubmitting(true);
    setError(null);

    try {
      await onSaved();
      setSuccess("Asset summary refreshed.");
      setNeedsRefresh(false);
    } catch {
      setError("The asset summary still could not be refreshed.");
      setNeedsRefresh(true);
    } finally {
      submissionInProgress.current = false;
      setIsSubmitting(false);
    }
  }

  return (
    <section
      className="detail-section manual-price-section"
      aria-labelledby="manual-price-title"
    >
      <h2 id="manual-price-title">Manual market price</h2>

      {latestSnapshot === null ? (
        <p className="market-unavailable">No manual price snapshot yet.</p>
      ) : (
        <dl className="manual-price-latest" aria-label="Latest price snapshot">
          <div>
            <dt>Latest price</dt>
            <dd>
              {formatCurrency(
                latestSnapshot.market_price_per_unit,
                latestSnapshot.currency,
              )}
            </dd>
          </div>
          <div>
            <dt>Currency</dt>
            <dd>{latestSnapshot.currency}</dd>
          </div>
          <div>
            <dt>Source</dt>
            <dd>Manual</dd>
          </div>
          <div>
            <dt>Confidence</dt>
            <dd>{formatConfidence(latestSnapshot.confidence)}</dd>
          </div>
          <div>
            <dt>Recorded</dt>
            <dd>{formatObservedAt(latestSnapshot.observed_at)}</dd>
          </div>
        </dl>
      )}

      <form className="manual-price-form" onSubmit={handleSubmit} noValidate>
        <label className="field">
          <span>Market price per unit (CAD)</span>
          <input
            required
            type="text"
            inputMode="decimal"
            value={pricePerUnit}
            onChange={(event) => {
              setPricePerUnit(event.target.value);
              setError(null);
              setSuccess(null);
            }}
            placeholder="1200.00"
            aria-describedby="manual-price-hint"
            disabled={isSubmitting || needsRefresh}
          />
          <small className="form-hint" id="manual-price-hint">
            Saving creates a new manual snapshot and updates the latest value.
          </small>
        </label>

        <button
          className="secondary-button"
          type="submit"
          disabled={isSubmitting || needsRefresh}
        >
          {isSubmitting ? "Saving price..." : "Save manual price"}
        </button>

        {error && (
          <p className="form-message form-message--error" role="alert">
            {error}
          </p>
        )}
        {needsRefresh && (
          <button
            className="secondary-button manual-price-refresh"
            type="button"
            disabled={isSubmitting}
            onClick={() => void handleRetryRefresh()}
          >
            Retry summary refresh
          </button>
        )}
        {success && (
          <p className="form-message form-message--success" role="status">
            {success}
          </p>
        )}
      </form>
    </section>
  );
}
