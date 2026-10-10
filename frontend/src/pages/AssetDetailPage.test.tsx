import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { deleteAsset, refreshAssetPrice } from "../api/assets";
import type { AssetResponse } from "../types/assets";
import { AssetDetailPage } from "./AssetDetailPage";

vi.mock("../api/assets", () => ({
  deleteAsset: vi.fn(),
  refreshAssetPrice: vi.fn(),
}));

vi.mock("../components/AssetDetailView", () => ({
  AssetDetailView: ({ asset }: { asset: AssetResponse }) => (
    <div>{asset.display_name} details</div>
  ),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("AssetDetailPage", () => {
  it("requires confirmation, deletes the asset, and returns to collection", async () => {
    vi.mocked(refreshAssetPrice).mockResolvedValue({
      id: 7,
      display_name: "Umbreon VMAX",
    } as AssetResponse);
    vi.mocked(deleteAsset).mockResolvedValue();

    render(
      <MemoryRouter initialEntries={["/assets/7"]}>
        <Routes>
          <Route path="assets/:assetId" element={<AssetDetailPage />} />
          <Route path="collection" element={<h1>Collection page</h1>} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByText("Umbreon VMAX details");
    fireEvent.click(screen.getByRole("button", { name: "Delete asset" }));

    expect(deleteAsset).not.toHaveBeenCalled();
    expect(screen.getByText("Delete Umbreon VMAX?")).toBeTruthy();

    fireEvent.click(
      screen.getByRole("button", { name: "Yes, delete asset" }),
    );

    await screen.findByRole("heading", { name: "Collection page" });
    expect(deleteAsset).toHaveBeenCalledWith(7);
  });
});
