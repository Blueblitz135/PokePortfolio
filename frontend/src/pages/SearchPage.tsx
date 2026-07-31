import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { createAsset, createPurchaseLot } from "../api/assets";
import { searchCards } from "../api/cardSearch";
import { ApiError } from "../api/client";
import { AddSearchedCardForm } from "../components/AddSearchedCardForm";
import { CardAddConfirmation } from "../components/CardAddConfirmation";
import { CardSearchForm } from "../components/CardSearchForm";
import { CardSearchResults } from "../components/CardSearchResults";
import type {
  CardAddDraft,
  CardSaveIssue,
  CardSavePhase,
  CardSearchResult,
} from "../types/cardSearch";
import { getCardSearchResultKey } from "../types/cardSearch";
import {
  buildCardAssetPayload,
  buildFirstPurchaseLotPayload,
} from "../utils/cardAssetPayload";

type WorkflowStage = "results" | "details" | "confirmation";

function isAbortError(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "name" in error &&
    error.name === "AbortError"
  );
}

function assetCreationIssue(error: unknown): CardSaveIssue {
  if (
    error instanceof ApiError &&
    error.status !== 408 &&
    error.status >= 400 &&
    error.status < 500
  ) {
    return {
      kind: "definite",
      message: `${error.message} Review the details and try again.`,
    };
  }

  return {
    kind: "ambiguous",
    message:
      "The card creation result could not be confirmed. Check Collection before submitting again so you do not create a duplicate.",
  };
}

function purchaseLotIssue(error: unknown): CardSaveIssue {
  if (
    error instanceof ApiError &&
    error.status !== 408 &&
    error.status >= 400 &&
    error.status < 500
  ) {
    return {
      kind: "partial_definite",
      message: `The card was added, but the purchase lot was rejected: ${error.message}`,
    };
  }

  return {
    kind: "partial_ambiguous",
    message:
      "The card was added, but the purchase request could not be confirmed. Inspect the asset before retrying so you do not create a duplicate purchase lot.",
  };
}

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [queryError, setQueryError] = useState<string | null>(null);
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [results, setResults] = useState<CardSearchResult[]>([]);
  const [selectedCard, setSelectedCard] =
    useState<CardSearchResult | null>(null);
  const [draft, setDraft] = useState<CardAddDraft | null>(null);
  const [workflowStage, setWorkflowStage] =
    useState<WorkflowStage>("results");
  const [savePhase, setSavePhase] = useState<CardSavePhase>("idle");
  const [saveIssue, setSaveIssue] = useState<CardSaveIssue | null>(null);
  const [createdAssetId, setCreatedAssetId] = useState<number | null>(null);
  const [ambiguousRetryConfirmed, setAmbiguousRetryConfirmed] =
    useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const searchRequestIdRef = useRef(0);
  const lastSubmittedQueryRef = useRef("");
  const selectedCardRef = useRef<CardSearchResult | null>(null);
  const saveLockRef = useRef(false);

  useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  function clearCardWorkflow() {
    selectedCardRef.current = null;
    setSelectedCard(null);
    setDraft(null);
    setWorkflowStage("results");
    setSavePhase("idle");
    setSaveIssue(null);
    setCreatedAssetId(null);
    setAmbiguousRetryConfirmed(false);
  }

  function cancelActiveSearch() {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    searchRequestIdRef.current += 1;
    setIsSearching(false);
  }

  async function runSearch(searchQuery: string) {
    cancelActiveSearch();
    const normalizedQuery = searchQuery.trim();

    if (normalizedQuery.length < 1 || normalizedQuery.length > 100) {
      setQueryError(
        "Search query must contain between 1 and 100 characters after trimming.",
      );
      return;
    }

    setQueryError(null);
    const isNewQuery =
      normalizedQuery !== lastSubmittedQueryRef.current;
    lastSubmittedQueryRef.current = normalizedQuery;
    setSubmittedQuery(normalizedQuery);
    setHasSearched(true);
    setSearchError(null);

    if (isNewQuery) {
      setResults([]);
      clearCardWorkflow();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const requestId = searchRequestIdRef.current + 1;
    searchRequestIdRef.current = requestId;
    setIsSearching(true);

    try {
      const nextResults = await searchCards(
        normalizedQuery,
        controller.signal,
      );
      if (requestId !== searchRequestIdRef.current) {
        return;
      }

      setResults(nextResults);
      const currentSelection = selectedCardRef.current;
      if (currentSelection !== null) {
        const matchingResult =
          nextResults.find(
            (result) =>
              getCardSearchResultKey(result) ===
              getCardSearchResultKey(currentSelection),
          ) ?? null;

        selectedCardRef.current = matchingResult;
        setSelectedCard(matchingResult);
        if (matchingResult === null) {
          setDraft(null);
          setWorkflowStage("results");
        }
      }
    } catch (error) {
      if (
        isAbortError(error) ||
        requestId !== searchRequestIdRef.current
      ) {
        return;
      }

      setSearchError(
        error instanceof Error
          ? error.message
          : "Card search could not be completed.",
      );
      setResults([]);
    } finally {
      if (requestId === searchRequestIdRef.current) {
        setIsSearching(false);
      }
    }
  }

  function handleSelectCard(card: CardSearchResult) {
    selectedCardRef.current = card;
    setSelectedCard(card);
    setDraft(null);
    setWorkflowStage("details");
    setSavePhase("idle");
    setSaveIssue(null);
    setCreatedAssetId(null);

    window.requestAnimationFrame(() => {
      document.getElementById("ownership-title")?.focus();
    });
  }

  function handleReview(nextDraft: CardAddDraft) {
    cancelActiveSearch();
    setDraft(nextDraft);
    setWorkflowStage("confirmation");
    setSaveIssue((currentIssue) =>
      currentIssue?.kind === "ambiguous" ? currentIssue : null,
    );
    setAmbiguousRetryConfirmed(false);
    window.requestAnimationFrame(() => {
      document.getElementById("confirmation-title")?.focus();
    });
  }

  async function handleConfirm() {
    if (
      selectedCard === null ||
      draft === null ||
      createdAssetId !== null ||
      (saveIssue?.kind === "ambiguous" &&
        !ambiguousRetryConfirmed) ||
      saveLockRef.current
    ) {
      return;
    }

    saveLockRef.current = true;
    setSaveIssue(null);
    setAmbiguousRetryConfirmed(false);
    setSavePhase("creating_asset");

    let assetId: number;
    try {
      const createdAsset = await createAsset(
        buildCardAssetPayload(selectedCard, draft),
      );
      assetId = createdAsset.id;
      setCreatedAssetId(assetId);
    } catch (error) {
      const issue = assetCreationIssue(error);
      setSaveIssue(issue);
      setAmbiguousRetryConfirmed(false);
      setSavePhase("idle");
      saveLockRef.current = false;
      return;
    }

    setSavePhase("creating_lot");
    try {
      await createPurchaseLot(
        assetId,
        buildFirstPurchaseLotPayload(draft),
      );
      setSavePhase("complete");
    } catch (error) {
      setSaveIssue(purchaseLotIssue(error));
      setSavePhase("partial");
    } finally {
      saveLockRef.current = false;
    }
  }

  async function handleRetryPurchaseLot(updatedDraft: CardAddDraft) {
    if (
      createdAssetId === null ||
      saveLockRef.current
    ) {
      return;
    }

    saveLockRef.current = true;
    setDraft(updatedDraft);
    setSaveIssue(null);
    setSavePhase("creating_lot");

    try {
      await createPurchaseLot(
        createdAssetId,
        buildFirstPurchaseLotPayload(updatedDraft),
      );
      setSavePhase("complete");
    } catch (error) {
      setSaveIssue(purchaseLotIssue(error));
      setSavePhase("partial");
    } finally {
      saveLockRef.current = false;
    }
  }

  const workflowLocked =
    workflowStage === "confirmation" ||
    savePhase === "creating_asset" ||
    savePhase === "creating_lot" ||
    savePhase === "partial" ||
    savePhase === "complete";

  return (
    <div className="app-shell search-page">
      <header className="app-header search-page-header">
        <div>
          <p className="eyebrow">Card discovery</p>
          <h1>Search cards</h1>
          <p className="intro">
            Find TCGdex card metadata, describe the copy you own, and review
            everything before adding it to your collection.
          </p>
        </div>
      </header>

      <section className="panel card-search-panel" aria-label="Card search">
        <CardSearchForm
          query={query}
          validationError={queryError}
          isSearching={isSearching}
          disabled={workflowLocked}
          onQueryChange={(nextQuery) => {
            setQuery(nextQuery);
            setQueryError(null);
          }}
          onSearch={() => void runSearch(query)}
        />
        <aside className="sealed-search-note">
          <strong>Looking for sealed products?</strong>
          <span>
            Sealed search is not available. Use the{" "}
            <Link to="/sealed-products#add-sealed-product">
              manual sealed-product workflow
            </Link>
            .
          </span>
        </aside>
      </section>

      {workflowStage !== "confirmation" && (
        <>
          <CardSearchResults
            results={results}
            submittedQuery={submittedQuery}
            hasSearched={hasSearched}
            isLoading={isSearching}
            error={searchError}
            selectedCard={selectedCard}
            disabled={workflowLocked}
            onSelect={handleSelectCard}
            onRetry={() => void runSearch(submittedQuery)}
          />

          {workflowStage === "details" && selectedCard && (
            <AddSearchedCardForm
              key={getCardSearchResultKey(selectedCard)}
              card={selectedCard}
              initialDraft={draft}
              onReview={handleReview}
              onCancel={clearCardWorkflow}
            />
          )}
        </>
      )}

      {workflowStage === "confirmation" && selectedCard && draft && (
        <CardAddConfirmation
          card={selectedCard}
          draft={draft}
          savePhase={savePhase}
          saveIssue={saveIssue}
          createdAssetId={createdAssetId}
          onBack={() => {
            setWorkflowStage("details");
            setSaveIssue((currentIssue) =>
              currentIssue?.kind === "ambiguous" ? currentIssue : null,
            );
            setAmbiguousRetryConfirmed(false);
          }}
          onConfirm={() => void handleConfirm()}
          onRetryLot={(updatedDraft) =>
            void handleRetryPurchaseLot(updatedDraft)
          }
          onStartOver={clearCardWorkflow}
          ambiguousRetryConfirmed={ambiguousRetryConfirmed}
          onAmbiguousRetryChange={setAmbiguousRetryConfirmed}
        />
      )}
    </div>
  );
}
