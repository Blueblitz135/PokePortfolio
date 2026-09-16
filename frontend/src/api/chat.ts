/** Typed request for the server-side portfolio analyst. */
import type {
  PortfolioChatMessage,
  PortfolioChatResponse,
} from "../types/chat";
import { requestJson } from "./client";

/** Submit bounded conversation history and receive an evidence-aware answer. */
export function askPortfolioAssistant(
  messages: PortfolioChatMessage[],
): Promise<PortfolioChatResponse> {
  return requestJson<PortfolioChatResponse>("/api/portfolio-chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
}
