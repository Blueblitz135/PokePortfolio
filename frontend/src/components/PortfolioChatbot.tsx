/** Conversational UI for server-side analysis of saved and external portfolio data. */
import { FormEvent, useState } from "react";

import { askPortfolioAssistant } from "../api/chat";
import type { AssetResponse } from "../types/assets";
import type {
  PortfolioChatMessage,
  PortfolioChatProviderStatus,
} from "../types/chat";


const QUICK_PROMPTS = [
  "How is my portfolio doing?",
  "Summarize the strongest and weakest trends.",
  "Which raw cards grew the most over the last 90 days?",
] as const;

const MAX_HISTORY_MESSAGES = 20;


/** Manage bounded chat history, provider coverage, loading, and error feedback. */
export function PortfolioChatbot({ onPricingUpdated }: { onPricingUpdated?: (assets: AssetResponse[]) => void }) {
  const [messages, setMessages] = useState<PortfolioChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [providers, setProviders] = useState<PortfolioChatProviderStatus[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Append a user turn, request analysis, and retain only bounded history. */
  async function sendMessage(content: string) {
    const trimmedContent = content.trim();
    if (!trimmedContent || isSending) {
      return;
    }

    const userMessage: PortfolioChatMessage = {
      role: "user",
      content: trimmedContent,
    };
    const requestMessages = [...messages, userMessage].slice(
      -MAX_HISTORY_MESSAGES,
    );
    setMessages(requestMessages);
    setDraft("");
    setError(null);
    setIsSending(true);

    try {
      const response = await askPortfolioAssistant(requestMessages);
      setMessages((current) =>
        [
          ...current,
          { role: "assistant", content: response.message } as const,
        ].slice(-MAX_HISTORY_MESSAGES),
      );
      setProviders(response.providers);
      if (response.assets) onPricingUpdated?.(response.assets);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The portfolio assistant could not answer right now.",
      );
    } finally {
      setIsSending(false);
    }
  }

  /** Submit the current draft through the shared send routine. */
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(draft);
  }

  return (
    <section className="portfolio-chat" aria-labelledby="portfolio-chat-title">
      <div className="portfolio-chat-header">
        <div>
          <p className="eyebrow">AI portfolio analyst</p>
          <h2 id="portfolio-chat-title">Ask about your collection</h2>
          <p>
            Uses your purchase records, current marketplace and verified store-sale
            estimates, price history, and TCGPlayer reference prices.
          </p>
        </div>
        <span className="portfolio-chat-ai-badge" aria-label="AI powered">
          AI
        </span>
      </div>

      {messages.length === 0 && (
        <div className="portfolio-chat-welcome">
          <p>
            Ask for a performance summary, asset growth, category trends, or
            gaps in your current pricing coverage.
          </p>
          <div className="portfolio-chat-prompts" aria-label="Suggested questions">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                className="portfolio-chat-prompt"
                type="button"
                key={prompt}
                disabled={isSending}
                onClick={() => void sendMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {messages.length > 0 && (
        <div className="portfolio-chat-messages" aria-live="polite">
          {messages.map((message, index) => (
            <article
              className={`portfolio-chat-message portfolio-chat-message--${message.role}`}
              key={`${message.role}-${index}`}
            >
              <strong>{message.role === "user" ? "You" : "Portfolio analyst"}</strong>
              <p>{message.content}</p>
            </article>
          ))}
          {isSending && (
            <p className="portfolio-chat-thinking" role="status">
              Reviewing your portfolio and market data...
            </p>
          )}
        </div>
      )}

      {providers.length > 0 && (
        <details className="portfolio-chat-sources">
          <summary>Data source coverage</summary>
          <ul>
            {providers.map((provider) => (
              <li key={provider.provider}>
                <span
                  className={`provider-state provider-state--${provider.state}`}
                >
                  {provider.provider}: {provider.state.replace("_", " ")}
                </span>
                <span>{provider.detail}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {error && (
        <p className="form-message form-message--error" role="alert">
          {error}
        </p>
      )}

      <form className="portfolio-chat-form" onSubmit={handleSubmit}>
        <label htmlFor="portfolio-chat-question">Your question</label>
        <div className="portfolio-chat-compose">
          <textarea
            id="portfolio-chat-question"
            value={draft}
            maxLength={2000}
            rows={3}
            placeholder="Ask how a card is performing or request a trend summary..."
            disabled={isSending}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button
            className="primary-button"
            type="submit"
            disabled={isSending || draft.trim().length === 0}
          >
            {isSending ? "Analyzing..." : "Ask analyst"}
          </button>
        </div>
      </form>

      <p className="portfolio-chat-disclaimer">
        Market estimates can be incomplete or delayed. This analysis is
        informational and is not financial advice.
      </p>
    </section>
  );
}
