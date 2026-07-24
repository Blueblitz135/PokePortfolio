from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.card_search import CardSearchResult
from app.services import card_search as card_search_service


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/cards", response_model=list[CardSearchResult])
async def search_cards(
    q: Annotated[str, Query(min_length=1, max_length=100)],
) -> list[CardSearchResult]:
    query = q.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Search query cannot be empty.",
        )

    try:
        return await card_search_service.search_cards(query)
    except card_search_service.CardSearchUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Card search is temporarily unavailable.",
        ) from None
