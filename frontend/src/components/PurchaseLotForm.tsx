import { type FormEvent, useState } from "react";

import { createPurchaseLot } from "../api/assets";

interface PurchaseLotFormProps {
  assetId: number;
  onSaved: () => Promise<void>;
}

function getToday(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function PurchaseLotForm({
  assetId,
  onSaved,
}: PurchaseLotFormProps) {
  const [purchaseDate, setPurchaseDate] = useState(getToday);
  const [quantity, setQuantity] = useState("1");
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      await createPurchaseLot(assetId, {
        purchase_date: purchaseDate,
        quantity: Number(quantity),
        purchase_price_per_unit: pricePerUnit,
        currency: "CAD",
      });
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "The purchase lot could not be added.",
      );
      setIsSubmitting(false);
      return;
    }

    setQuantity("1");
    setPricePerUnit("");

    try {
      await onSaved();
      setSuccess("Purchase lot added.");
    } catch {
      setError(
        "The purchase lot was added, but the summary could not be refreshed. Reload the page to see the latest values.",
      );
    }

    setIsSubmitting(false);
  }

  return (
    <section className="detail-section" aria-labelledby="add-lot-title">
      <h3 id="add-lot-title">Add purchase lot</h3>
      <form className="form-grid form-grid--compact" onSubmit={handleSubmit}>
        <label className="field">
          <span>Purchase date</span>
          <input
            required
            type="date"
            value={purchaseDate}
            onChange={(event) => setPurchaseDate(event.target.value)}
          />
        </label>

        <label className="field">
          <span>Quantity</span>
          <input
            required
            type="number"
            min="1"
            step="1"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
        </label>

        <label className="field">
          <span>Price per unit (CAD)</span>
          <input
            required
            type="number"
            min="0"
            step="0.01"
            value={pricePerUnit}
            onChange={(event) => setPricePerUnit(event.target.value)}
            placeholder="750.00"
          />
        </label>

        {error && (
          <p className="form-message form-message--error field--wide" role="alert">
            {error}
          </p>
        )}
        {success && (
          <p
            className="form-message form-message--success field--wide"
            role="status"
          >
            {success}
          </p>
        )}

        <button
          className="secondary-button field--wide"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Adding lot..." : "Add purchase lot"}
        </button>
      </form>
    </section>
  );
}
