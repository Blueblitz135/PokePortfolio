import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { askPortfolioAssistant } from "../api/chat";
import { PortfolioChatbot } from "./PortfolioChatbot";


vi.mock("../api/chat", () => ({
  askPortfolioAssistant: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("PortfolioChatbot", () => {
  it("sends a suggested question and shows the answer with source coverage", async () => {
    vi.mocked(askPortfolioAssistant).mockResolvedValue({
      message: "Your raw cards have a positive supported trend.",
      generated_at: "2026-09-13T12:00:00Z",
      providers: [
        {
          provider: "JustTCG",
          state: "available",
          detail: "Matched 1 of 1 raw cards for 90d history.",
        },
      ],
    });

    render(<PortfolioChatbot />);
    fireEvent.click(
      screen.getByRole("button", { name: "How is my portfolio doing?" }),
    );

    expect(
      await screen.findByText("Your raw cards have a positive supported trend."),
    ).toBeTruthy();
    expect(askPortfolioAssistant).toHaveBeenCalledWith([
      { role: "user", content: "How is my portfolio doing?" },
    ]);

    fireEvent.click(screen.getByText("Data source coverage"));
    expect(screen.getByText(/JustTCG: available/)).toBeTruthy();
  });

  it("shows a configuration error returned by the backend", async () => {
    vi.mocked(askPortfolioAssistant).mockRejectedValue(
      new Error("Portfolio assistant is not configured."),
    );

    render(<PortfolioChatbot />);
    fireEvent.change(screen.getByLabelText("Your question"), {
      target: { value: "Summarize my collection" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask analyst" }));

    expect(
      await screen.findByText("Portfolio assistant is not configured."),
    ).toBeTruthy();
  });
});
