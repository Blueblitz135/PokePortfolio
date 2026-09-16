/** API contracts for the portfolio analyst conversation and provider coverage. */
export type PortfolioChatRole = "user" | "assistant";

/** One bounded user or assistant conversation turn. */
export interface PortfolioChatMessage {
  role: PortfolioChatRole;
  content: string;
}

export type PortfolioChatProviderState =
  | "available"
  | "partial"
  | "unavailable"
  | "not_configured"
  | "not_needed";

/** Human-readable coverage result for one external market-data provider. */
export interface PortfolioChatProviderStatus {
  provider: string;
  state: PortfolioChatProviderState;
  detail: string;
}

/** Generated answer and evidence-provider statuses for one turn. */
export interface PortfolioChatResponse {
  assets?: import("./assets").AssetResponse[];
  message: string;
  generated_at: string;
  providers: PortfolioChatProviderStatus[];
}
