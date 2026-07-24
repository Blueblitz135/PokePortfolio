import asyncio

import httpx
import pytest

from app.adapters.tcgdex import TCGdexAdapter, TCGdexError
from app.schemas.card_search import CardSearchResult


def _search(
    adapter: TCGdexAdapter, query: str
) -> list[CardSearchResult]:
    return asyncio.run(adapter.search_cards(query))


def test_search_cards_normalizes_tcgdex_results() -> None:
    requested_paths: list[str] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requested_paths.append(request.url.path)

        if request.url.path == "/v2/en/cards":
            assert request.url.params["name"] == "Umbreon VMAX"
            assert request.url.params["pagination:page"] == "1"
            assert request.url.params["pagination:itemsPerPage"] == "20"
            return httpx.Response(
                200,
                json=[
                    {
                        "id": "swsh7-215",
                        "localId": "215",
                        "name": "Umbreon VMAX",
                        "image": "https://assets.tcgdex.net/en/swsh/swsh7/215",
                    }
                ],
            )

        if request.url.path == "/v2/en/cards/swsh7-215":
            return httpx.Response(
                200,
                json={
                    "id": "swsh7-215",
                    "localId": "215",
                    "name": "Umbreon VMAX",
                    "rarity": "Secret Rare",
                    "image": "https://assets.tcgdex.net/en/swsh/swsh7/215",
                    "set": {
                        "id": "swsh7",
                        "name": "Evolving Skies",
                        "cardCount": {"official": 203, "total": 237},
                    },
                    "pricing": {"cardmarket": {"avg": 999.99}},
                },
            )

        if request.url.path == "/v2/en/sets/swsh7":
            return httpx.Response(
                200,
                json={"id": "swsh7", "releaseDate": "2021-08-27"},
            )

        raise AssertionError(f"Unexpected request: {request.url}")

    adapter = TCGdexAdapter(
        base_url="https://api.tcgdex.net/v2/en",
        transport=httpx.MockTransport(handle_request),
    )

    results = _search(adapter, "  Umbreon VMAX  ")

    assert [result.model_dump(mode="json") for result in results] == [
        {
            "external_source": "tcgdex",
            "external_id": "swsh7-215",
            "name": "Umbreon VMAX",
            "set_name": "Evolving Skies",
            "set_id": "swsh7",
            "year": 2021,
            "card_number": "215",
            "set_total": "203",
            "rarity": "Secret Rare",
            "image_url": (
                "https://assets.tcgdex.net/en/swsh/swsh7/215/high.webp"
            ),
        }
    ]
    assert requested_paths == [
        "/v2/en/cards",
        "/v2/en/cards/swsh7-215",
        "/v2/en/sets/swsh7",
    ]


def test_search_cards_returns_empty_list_when_tcgdex_has_no_results() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/en/cards"
        return httpx.Response(200, json=[])

    adapter = TCGdexAdapter(
        base_url="https://api.tcgdex.net/v2/en",
        transport=httpx.MockTransport(handle_request),
    )

    assert _search(adapter, "missing card") == []


def test_search_cards_allows_missing_optional_metadata() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/en/cards":
            return httpx.Response(200, json=[{"id": "base1-1"}])
        if request.url.path == "/v2/en/cards/base1-1":
            return httpx.Response(
                200,
                json={
                    "id": "base1-1",
                    "localId": 1,
                    "name": "Alakazam",
                    "set": {
                        "id": "base1",
                        "name": "Base Set",
                    },
                },
            )
        if request.url.path == "/v2/en/sets/base1":
            return httpx.Response(
                200,
                json={"id": "base1", "releaseDate": "1999-01-09"},
            )
        raise AssertionError(f"Unexpected request: {request.url}")

    adapter = TCGdexAdapter(
        base_url="https://api.tcgdex.net/v2/en",
        transport=httpx.MockTransport(handle_request),
    )

    result = _search(adapter, "Alakazam")[0]

    assert result.year == 1999
    assert result.card_number == "1"
    assert result.set_total is None
    assert result.rarity is None
    assert result.image_url is None


def test_search_cards_raises_adapter_error_for_upstream_failure() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    adapter = TCGdexAdapter(
        base_url="https://api.tcgdex.net/v2/en",
        transport=httpx.MockTransport(handle_request),
    )

    with pytest.raises(TCGdexError):
        _search(adapter, "Pikachu")
