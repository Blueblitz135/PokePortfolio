import type { CardSearchResult } from "../types/cardSearch";
import { requestJson } from "./client";

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
