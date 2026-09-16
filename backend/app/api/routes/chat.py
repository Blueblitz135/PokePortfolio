"""Expose the AI portfolio-analysis endpoint and translate provider failures."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.openai_responses import (
    OpenAIResponsesConfigurationError,
    OpenAIResponsesError,
)
from app.db.session import get_db
from app.schemas.chat import PortfolioChatRequest, PortfolioChatResponse
from app.services import portfolio_chat as portfolio_chat_service


router = APIRouter(prefix="/portfolio-chat", tags=["portfolio chat"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=PortfolioChatResponse)
async def create_portfolio_chat_response(
    data: PortfolioChatRequest, db: DatabaseSession
) -> PortfolioChatResponse:
    """Build portfolio context and return a model-generated answer."""

    try:
        return await portfolio_chat_service.answer_portfolio_question(db, data)
    except OpenAIResponsesConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Portfolio assistant is not configured. Replace the placeholder "
                "OPENAI_API_KEY in backend/.env."
            ),
        ) from None
    except OpenAIResponsesError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Portfolio assistant is temporarily unavailable.",
        ) from None
