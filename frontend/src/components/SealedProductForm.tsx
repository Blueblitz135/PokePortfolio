/** Create an upload-first sealed-product asset using manually entered metadata. */
import { type FormEvent, useState } from "react";

import { createSealedProduct } from "../api/assets";
import {
  isSealedProductAsset,
  SEALED_PRODUCT_TYPE_OPTIONS,
  type SealedProductAsset,
  type SealedProductType,
} from "../types/assets";

interface SealedProductFormProps {
  onCreated: (asset: SealedProductAsset) => void;
}

/** Validate sealed metadata, persist the asset, and report the new identifier. */
export function SealedProductForm({ onCreated }: SealedProductFormProps) {
  const [productName, setProductName] = useState("");
  const [setName, setSetName] = useState("");
  const [year, setYear] = useState("");
  const [productType, setProductType] =
    useState<SealedProductType>("booster_box");
  const [isPokemonCenterExclusive, setIsPokemonCenterExclusive] =
    useState(false);
  const [userNote, setUserNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  /** Validate form fields, create the asset, and clear the form on success. */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    const normalizedProductName = productName.trim();
    if (!normalizedProductName) {
      setError("Product name is required.");
      setIsSubmitting(false);
      return;
    }

    try {
      const createdAsset = await createSealedProduct({
        asset_type: "sealed_product",
        display_name: normalizedProductName,
        user_note: userNote.trim() || null,
        sealed_product_metadata: {
          product_name: normalizedProductName,
          set_name: setName.trim() || null,
          year: year ? Number(year) : null,
          sealed_product_type: productType,
          is_pokemon_center_exclusive: isPokemonCenterExclusive,
        },
      });

      if (!isSealedProductAsset(createdAsset)) {
        throw new Error("The API returned an unexpected asset type.");
      }

      onCreated(createdAsset);
      setProductName("");
      setSetName("");
      setYear("");
      setProductType("booster_box");
      setIsPokemonCenterExclusive(false);
      setUserNote("");
      setSuccess(`${createdAsset.display_name} was added.`);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "The sealed product could not be added.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel create-panel" aria-labelledby="add-product-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">New asset</p>
          <h2 id="add-product-title">Add a sealed product</h2>
        </div>
      </div>

      <form className="form-grid" onSubmit={handleSubmit}>
        <label className="field field--wide">
          <span>Product name</span>
          <input
            required
            maxLength={255}
            value={productName}
            onChange={(event) => setProductName(event.target.value)}
            placeholder="Evolving Skies Booster Box"
          />
        </label>

        <label className="field">
          <span>Product type</span>
          <select
            value={productType}
            onChange={(event) =>
              setProductType(event.target.value as SealedProductType)
            }
          >
            {SEALED_PRODUCT_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Set name</span>
          <input
            maxLength={255}
            value={setName}
            onChange={(event) => setSetName(event.target.value)}
            placeholder="Evolving Skies"
          />
        </label>

        <label className="field">
          <span>Release year</span>
          <input
            type="number"
            min="1996"
            max="2100"
            value={year}
            onChange={(event) => setYear(event.target.value)}
            placeholder="2021"
          />
        </label>

        <label className="checkbox-field">
          <input
            type="checkbox"
            checked={isPokemonCenterExclusive}
            onChange={(event) =>
              setIsPokemonCenterExclusive(event.target.checked)
            }
          />
          <span>Pokémon Center exclusive</span>
        </label>

        <label className="field field--wide">
          <span>Note</span>
          <textarea
            rows={3}
            value={userNote}
            onChange={(event) => setUserNote(event.target.value)}
            placeholder="Optional note about this product"
          />
        </label>

        <p className="form-hint field--wide">
          Booster bundles always represent 6 packs. Pack art and product
          artwork versions are not tracked.
        </p>

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
          className="primary-button field--wide"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Adding product..." : "Add sealed product"}
        </button>
      </form>
    </section>
  );
}
