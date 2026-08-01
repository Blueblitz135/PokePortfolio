import {
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  deletePurchaseLot,
  updatePurchaseLot,
} from "../api/assets";
import { useCurrencyFormatter } from "../hooks/useCurrencyFormatter";
import type { PurchaseLot } from "../types/assets";

interface PurchaseLotManagerProps {
  assetName: string;
  lots: PurchaseLot[];
  onChanged: () => Promise<void>;
}

function formatPurchaseDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-CA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getLotDescription(lot: PurchaseLot): string {
  return `${formatPurchaseDate(lot.purchase_date)}, ${lot.quantity} ${
    lot.quantity === 1 ? "unit" : "units"
  }`;
}

export function PurchaseLotManager({
  assetName,
  lots,
  onChanged,
}: PurchaseLotManagerProps) {
  const formatCurrency = useCurrencyFormatter();
  const sortedLots = useMemo(
    () =>
      [...lots].sort(
        (first, second) =>
          second.purchase_date.localeCompare(first.purchase_date) ||
          second.id - first.id,
      ),
    [lots],
  );
  const [editingLotId, setEditingLotId] = useState<number | null>(null);
  const [deleteLotId, setDeleteLotId] = useState<number | null>(null);
  const [purchaseDate, setPurchaseDate] = useState("");
  const [quantity, setQuantity] = useState("");
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [isMutating, setIsMutating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [needsRefresh, setNeedsRefresh] = useState(false);
  const managerRef = useRef<HTMLDivElement>(null);
  const editDateInputRef = useRef<HTMLInputElement>(null);
  const deleteHeadingRef = useRef<HTMLHeadingElement>(null);

  const editingLot =
    sortedLots.find((lot) => lot.id === editingLotId) ?? null;
  const deleteLot =
    sortedLots.find((lot) => lot.id === deleteLotId) ?? null;

  useEffect(() => {
    if (editingLotId !== null && editingLot === null) {
      setEditingLotId(null);
    }
    if (deleteLotId !== null && deleteLot === null) {
      setDeleteLotId(null);
    }
  }, [deleteLot, deleteLotId, editingLot, editingLotId]);

  useEffect(() => {
    if (editingLot !== null) {
      editDateInputRef.current?.focus();
    }
  }, [editingLot]);

  useEffect(() => {
    if (deleteLot !== null) {
      deleteHeadingRef.current?.focus();
    }
  }, [deleteLot]);

  function focusEditButton(lotId: number) {
    window.requestAnimationFrame(() => {
      managerRef.current
        ?.querySelector<HTMLButtonElement>(`[data-edit-lot="${lotId}"]`)
        ?.focus();
    });
  }

  function startEditing(lot: PurchaseLot) {
    if (isMutating || needsRefresh) {
      return;
    }

    setDeleteLotId(null);
    setError(null);
    setSuccess(null);
    setEditingLotId(lot.id);
    setPurchaseDate(lot.purchase_date);
    setQuantity(String(lot.quantity));
    setPricePerUnit(lot.purchase_price_per_unit);
  }

  function cancelEditing() {
    const lotId = editingLotId;
    setEditingLotId(null);
    setError(null);

    if (lotId !== null) {
      focusEditButton(lotId);
    }
  }

  function startDeleting(lot: PurchaseLot) {
    if (isMutating || needsRefresh) {
      return;
    }

    setEditingLotId(null);
    setError(null);
    setSuccess(null);
    setDeleteLotId(lot.id);
  }

  function cancelDeleting() {
    const lotId = deleteLotId;
    setDeleteLotId(null);
    setError(null);

    if (lotId !== null) {
      window.requestAnimationFrame(() => {
        managerRef.current
          ?.querySelector<HTMLButtonElement>(`[data-delete-lot="${lotId}"]`)
          ?.focus();
      });
    }
  }

  async function refreshAfterMutation(
    successMessage: string,
    refreshFailureMessage: string,
  ) {
    try {
      await onChanged();
      setSuccess(successMessage);
      setNeedsRefresh(false);
    } catch {
      setError(refreshFailureMessage);
      setNeedsRefresh(true);
    }
  }

  async function handleEditSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (editingLot === null) {
      return;
    }

    setIsMutating(true);
    setError(null);
    setSuccess(null);
    setNeedsRefresh(false);

    try {
      await updatePurchaseLot(editingLot.id, {
        purchase_date: purchaseDate,
        quantity: Number(quantity),
        purchase_price_per_unit: pricePerUnit,
      });
    } catch (updateError) {
      setError(
        updateError instanceof Error
          ? updateError.message
          : "The purchase lot could not be updated.",
      );
      setIsMutating(false);
      return;
    }

    const updatedLotId = editingLot.id;
    setEditingLotId(null);
    await refreshAfterMutation(
      "Purchase lot updated.",
      "The purchase lot was updated, but the asset summary could not be refreshed.",
    );
    setIsMutating(false);
    focusEditButton(updatedLotId);
  }

  async function handleDelete() {
    if (deleteLot === null) {
      return;
    }

    setIsMutating(true);
    setError(null);
    setSuccess(null);
    setNeedsRefresh(false);

    try {
      await deletePurchaseLot(deleteLot.id);
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "The purchase lot could not be deleted.",
      );
      setIsMutating(false);
      return;
    }

    setDeleteLotId(null);
    await refreshAfterMutation(
      "Purchase lot deleted.",
      "The purchase lot was deleted, but the asset summary could not be refreshed.",
    );
    setIsMutating(false);
    window.requestAnimationFrame(() => {
      document.getElementById("purchase-lots-title")?.focus();
    });
  }

  async function handleRetryRefresh() {
    setIsMutating(true);
    setError(null);

    try {
      await onChanged();
      setNeedsRefresh(false);
      setSuccess("Asset summary refreshed.");
    } catch {
      setError("The asset summary still could not be refreshed.");
      setNeedsRefresh(true);
    } finally {
      setIsMutating(false);
    }
  }

  return (
    <div className="purchase-lot-manager" ref={managerRef}>
      {error && (
        <div className="mutation-feedback" role="alert">
          <p className="form-message form-message--error">{error}</p>
          {needsRefresh && (
            <button
              className="secondary-button compact-button"
              type="button"
              disabled={isMutating}
              onClick={() => void handleRetryRefresh()}
            >
              Retry refresh
            </button>
          )}
        </div>
      )}
      {success && (
        <p className="form-message form-message--success" role="status">
          {success}
        </p>
      )}

      {sortedLots.length === 0 ? (
        <p className="inline-empty-state">
          No purchase lots yet. Add the first purchase below.
        </p>
      ) : (
        <div className="table-scroll">
          <table>
            <caption className="visually-hidden">
              Purchase lots for {assetName}
            </caption>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Quantity</th>
                <th scope="col">Price per unit</th>
                <th scope="col">Currency</th>
                <th scope="col">Lot cost</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedLots.map((lot) => {
                const description = getLotDescription(lot);
                const lotCost =
                  Number(lot.purchase_price_per_unit) * lot.quantity;

                return (
                  <tr key={lot.id}>
                    <td>{formatPurchaseDate(lot.purchase_date)}</td>
                    <td>{lot.quantity}</td>
                    <td>
                      {formatCurrency(
                        lot.purchase_price_per_unit,
                        lot.currency,
                      )}
                    </td>
                    <td>{lot.currency}</td>
                    <td>{formatCurrency(lotCost, lot.currency)}</td>
                    <td>
                      <div className="purchase-lot-actions">
                        <button
                          className="secondary-button compact-button"
                          type="button"
                          data-edit-lot={lot.id}
                          disabled={isMutating || needsRefresh}
                          aria-label={`Edit purchase lot from ${description}`}
                          onClick={() => startEditing(lot)}
                        >
                          Edit
                        </button>
                        <button
                          className="danger-button compact-button"
                          type="button"
                          data-delete-lot={lot.id}
                          disabled={isMutating || needsRefresh}
                          aria-label={`Delete purchase lot from ${description}`}
                          onClick={() => startDeleting(lot)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {editingLot && (
        <section className="lot-editor" aria-labelledby="edit-lot-title">
          <h3 id="edit-lot-title">Edit purchase lot</h3>
          <form
            className="form-grid form-grid--compact"
            onSubmit={(event) => void handleEditSubmit(event)}
          >
            <label className="field">
              <span>Purchase date</span>
              <input
                ref={editDateInputRef}
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
              <span>Price per unit ({editingLot.currency})</span>
              <input
                required
                type="number"
                min="0"
                step="0.01"
                value={pricePerUnit}
                onChange={(event) => setPricePerUnit(event.target.value)}
              />
            </label>

            <div className="lot-form-actions field--wide">
              <button
                className="primary-button"
                type="submit"
                disabled={isMutating}
              >
                {isMutating ? "Saving..." : "Save changes"}
              </button>
              <button
                className="secondary-button"
                type="button"
                disabled={isMutating}
                onClick={cancelEditing}
              >
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}

      {deleteLot && (
        <section
          className="lot-delete-confirmation"
          aria-labelledby="delete-lot-title"
        >
          <h3 id="delete-lot-title" ref={deleteHeadingRef} tabIndex={-1}>
            Delete this purchase lot?
          </h3>
          <p>
            {getLotDescription(deleteLot)} at{" "}
            {formatCurrency(
              deleteLot.purchase_price_per_unit,
              deleteLot.currency,
            )}{" "}
            per unit. This
            action cannot be undone.
          </p>
          <div className="lot-form-actions">
            <button
              className="danger-button"
              type="button"
              disabled={isMutating}
              onClick={() => void handleDelete()}
            >
              {isMutating ? "Deleting..." : "Confirm delete"}
            </button>
            <button
              className="secondary-button"
              type="button"
              disabled={isMutating}
              onClick={cancelDeleting}
            >
              Cancel
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
