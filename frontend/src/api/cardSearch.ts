/** Typed request for the backend's normalized TCGdex card search. */
import type { CardSearchResult } from "../types/cardSearch";
import { requestJson } from "./client";

/** Search card metadata and allow callers to cancel stale requests. */
export function searchCards(
  query: string,
  signal?: AbortSignal,
): Promise<CardSearchResult[]> {
  const searchParams = new URLSearchParams({ q: query });

  return requestJson<CardSearchResult[]>(
    `/api/search/cards?${searchParams.toString()}`,
    { signal },
  );
}
