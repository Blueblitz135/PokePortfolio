from app.adapters.tcgdex import TCGdexAdapter, TCGdexError
from app.config import settings
from app.schemas.card_search import CardSearchResult


MAX_NAME_SEARCH_ATTEMPTS = 4


class CardSearchUnavailableError(Exception):
    """Raised when no card metadata provider is available."""


tcgdex_adapter = TCGdexAdapter(
    base_url=settings.tcgdex_base_url,
    timeout_seconds=settings.tcgdex_timeout_seconds,
    max_results=settings.tcgdex_search_limit,
)


async def search_cards(query: str) -> list[CardSearchResult]:
    normalized_query = query.strip()
    if not normalized_query:
        return []

    try:
        for name_query in _name_search_queries(normalized_query):
            results = await tcgdex_adapter.search_cards(name_query)
            if results:
                return _best_matches(results, normalized_query)
        return []
    except TCGdexError as exc:
        raise CardSearchUnavailableError from exc


def _name_search_queries(query: str) -> list[str]:
    words = query.split()
    minimum_word_count = max(1, len(words) - MAX_NAME_SEARCH_ATTEMPTS + 1)
    return [
        " ".join(words[:word_count])
        for word_count in range(len(words), minimum_word_count - 1, -1)
    ]


def _best_matches(
    results: list[CardSearchResult], original_query: str
) -> list[CardSearchResult]:
    query_terms = original_query.casefold().split()
    scored_results = [
        (_match_score(result, query_terms), result) for result in results
    ]
    complete_matches = [
        result
        for score, result in scored_results
        if score == len(query_terms)
    ]
    if complete_matches:
        return complete_matches

    scored_results.sort(key=lambda item: item[0], reverse=True)
    return [result for _, result in scored_results]


def _match_score(result: CardSearchResult, query_terms: list[str]) -> int:
    structured_number = (
        f"{result.card_number}/{result.set_total}"
        if result.set_total is not None
        else result.card_number
    )
    searchable_text = " ".join(
        [
            result.name,
            result.set_name,
            result.set_id,
            structured_number,
            result.rarity or "",
        ]
    ).casefold()
    return sum(term in searchable_text for term in query_terms)
