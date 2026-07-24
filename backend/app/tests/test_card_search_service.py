import asyncio

import pytest

from app.adapters.tcgdex import TCGdexError
from app.models.enums import ExternalSource
from app.schemas.card_search import CardSearchResult
from app.services import card_search as card_search_service


def _result(set_name: str, set_id: str) -> CardSearchResult:
    return CardSearchResult(
        external_source=ExternalSource.TCGDEX,
        external_id=f"{set_id}-215",
        name="Umbreon VMAX",
        set_name=set_name,
        set_id=set_id,
        year=2021,
        card_number="215",
        set_total="203",
        rarity="Secret Rare",
        image_url=None,
    )


def test_search_cards_handles_trailing_set_terms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queries: list[str] = []

    class FakeAdapter:
        async def search_cards(self, query: str) -> list[CardSearchResult]:
            queries.append(query)
            if query == "Umbreon VMAX":
                return [
                    _result("Brilliant Stars", "swsh9"),
                    _result("Evolving Skies", "swsh7"),
                ]
            return []

    monkeypatch.setattr(card_search_service, "tcgdex_adapter", FakeAdapter())

    results = asyncio.run(
        card_search_service.search_cards("Umbreon VMAX Evolving Skies")
    )

    assert queries == [
        "Umbreon VMAX Evolving Skies",
        "Umbreon VMAX Evolving",
        "Umbreon VMAX",
    ]
    assert [result.set_id for result in results] == ["swsh7"]


def test_search_cards_translates_tcgdex_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class UnavailableAdapter:
        async def search_cards(self, query: str) -> list[CardSearchResult]:
            raise TCGdexError

    monkeypatch.setattr(
        card_search_service, "tcgdex_adapter", UnavailableAdapter()
    )

    with pytest.raises(card_search_service.CardSearchUnavailableError):
        asyncio.run(card_search_service.search_cards("Pikachu"))
