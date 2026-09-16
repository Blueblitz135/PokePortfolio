"""Validate portfolio-chat messages, provider statuses, and generated answers."""

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.schemas.domain import DomainSchema
from app.schemas.assets import AssetResponse


ChatRole = Literal["user", "assistant"]
ProviderState = Literal[
    "available", "partial", "unavailable", "not_configured", "not_needed"
]


class PortfolioChatMessage(DomainSchema):
    """One user or assistant turn supplied to the portfolio analyst."""

    role: ChatRole
    content: str = Field(min_length=1, max_length=2_000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        """Remove surrounding whitespace before length and emptiness checks."""

        return value.strip()


class PortfolioChatRequest(DomainSchema):
    """Bounded conversation history whose newest message must come from the user."""

    messages: list[PortfolioChatMessage] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def require_latest_user_message(self) -> "PortfolioChatRequest":
        """Prevent requests that ask the model to continue without new user input."""

        if self.messages[-1].role != "user":
            raise ValueError("The final chat message must come from the user.")
        return self


class PortfolioChatProviderStatus(DomainSchema):
    """Explain whether an external market provider contributed to an answer."""

    provider: str
    state: ProviderState
    detail: str


class PortfolioChatResponse(DomainSchema):
    """Generated answer with timestamped market-data coverage information."""

    message: str
    generated_at: datetime
    providers: list[PortfolioChatProviderStatus]
    assets: list[AssetResponse] = Field(default_factory=list)
