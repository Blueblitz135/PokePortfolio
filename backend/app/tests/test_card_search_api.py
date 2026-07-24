import pytest
from fastapi.testclient import TestClient

from app.api.routes import search as search_route
from app.main import app
from app.models.enums import ExternalSource
from app.schemas.card_search import CardSearchResult


client = TestClient(app)


def test_search_cards_endpoint_returns_normalized_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_search_cards(query: str) -> list[CardSearchResult]:
        assert query == "Umbreon VMAX"
        return [
            CardSearchResult(
                external_source=ExternalSource.TCGDEX,
                external_id="swsh7-215",
                name="Umbreon VMAX",
                set_name="Evolving Skies",
                set_id="swsh7",
                year=2021,
                card_number="215",
                set_total="203",
                rarity="Secret Rare",
                image_url=(
                    "https://assets.tcgdex.net/en/swsh/swsh7/215/high.webp"
                ),
            )
        ]

    monkeypatch.setattr(
        search_route.card_search_service, "search_cards", fake_search_cards
    )

    response = client.get("/api/search/cards", params={"q": "  Umbreon VMAX  "})

    assert response.status_code == 200
    assert response.json() == [
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
    assert "pricing" not in response.json()[0]


def test_search_cards_endpoint_returns_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_search_cards(query: str) -> list[CardSearchResult]:
        return []

    monkeypatch.setattr(
        search_route.card_search_service, "search_cards", fake_search_cards
    )

    response = client.get("/api/search/cards", params={"q": "missing card"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("params", [{}, {"q": "   "}])
def test_search_cards_endpoint_requires_query(params: dict[str, str]) -> None:
    response = client.get("/api/search/cards", params=params)

    assert response.status_code == 422


def test_search_cards_endpoint_handles_provider_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unavailable_search(query: str) -> list[CardSearchResult]:
        raise search_route.card_search_service.CardSearchUnavailableError

    monkeypatch.setattr(
        search_route.card_search_service, "search_cards", unavailable_search
    )

    response = client.get("/api/search/cards", params={"q": "Pikachu"})

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Card search is temporarily unavailable."
    }
