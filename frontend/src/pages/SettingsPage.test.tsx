import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { PortfolioPreferencesProvider } from "../preferences/PortfolioPreferencesProvider";
import { PORTFOLIO_PREFERENCES_STORAGE_KEY } from "../preferences/portfolioPreferences";
import { SettingsPage } from "./SettingsPage";

afterEach(() => {
  cleanup();
  window.localStorage.clear();
});

describe("SettingsPage", () => {
  it("saves the selected collection default and keeps unsupported currencies disabled", () => {
    render(
      <PortfolioPreferencesProvider>
        <SettingsPage />
      </PortfolioPreferencesProvider>,
    );

    const defaultFilter = screen.getByLabelText(
      "Default collection filter",
    ) as HTMLSelectElement;
    fireEvent.change(defaultFilter, { target: { value: "sealed_product" } });
    fireEvent.click(
      screen.getByRole("button", { name: "Save preferences" }),
    );

    expect(
      JSON.parse(
        window.localStorage.getItem(PORTFOLIO_PREFERENCES_STORAGE_KEY) ?? "",
      ),
    ).toEqual({
      version: 1,
      displayCurrency: "CAD",
      defaultAssetTypeFilter: "sealed_product",
    });
    expect(screen.getByRole("status").textContent).toContain("saved");
    expect(
      (
        screen.getByRole("option", {
          name: /USD - Unavailable until currency conversion is added/,
        }) as HTMLOptionElement
      ).disabled,
    ).toBe(true);
  });

  it("resets stored preferences to CAD and the all-assets filter", () => {
    window.localStorage.setItem(
      PORTFOLIO_PREFERENCES_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        displayCurrency: "CAD",
        defaultAssetTypeFilter: "raw_card",
      }),
    );

    render(
      <PortfolioPreferencesProvider>
        <SettingsPage />
      </PortfolioPreferencesProvider>,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Reset to defaults" }),
    );

    expect(
      JSON.parse(
        window.localStorage.getItem(PORTFOLIO_PREFERENCES_STORAGE_KEY) ?? "",
      ),
    ).toEqual({
      version: 1,
      displayCurrency: "CAD",
      defaultAssetTypeFilter: "all",
    });
  });
});
