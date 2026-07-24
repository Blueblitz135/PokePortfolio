import { type ChangeEvent, type FormEvent, useRef, useState } from "react";

import { uploadAssetImage } from "../api/assets";

interface AssetImageUploadProps {
  assetId: number;
  onSaved: () => Promise<void>;
}

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024;

export function AssetImageUpload({
  assetId,
  onSaved,
}: AssetImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    setError(null);
    setSuccess(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!file) {
      setError("Choose an image before uploading.");
      return;
    }

    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      setError("Images must be 5 MB or smaller.");
      return;
    }

    setIsSubmitting(true);

    try {
      await uploadAssetImage(assetId, file);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "The image could not be uploaded.",
      );
      setIsSubmitting(false);
      return;
    }

    setFile(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }

    try {
      await onSaved();
      setSuccess("Primary image updated.");
    } catch {
      setError(
        "The image was uploaded, but the product could not be refreshed. Reload the page to see the new image.",
      );
    }

    setIsSubmitting(false);
  }

  return (
    <section className="detail-section" aria-labelledby="upload-image-title">
      <h3 id="upload-image-title">Product image</h3>
      <form className="upload-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Choose an image</span>
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />
        </label>
        <p className="form-hint">JPG, JPEG, PNG, or WebP. Maximum 5 MB.</p>

        {error && (
          <p className="form-message form-message--error" role="alert">
            {error}
          </p>
        )}
        {success && (
          <p className="form-message form-message--success" role="status">
            {success}
          </p>
        )}

        <button
          className="secondary-button"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Uploading..." : "Upload primary image"}
        </button>
      </form>
    </section>
  );
}
