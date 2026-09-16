"""Schema for the backend availability response."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Stable health-check payload consumed by the frontend status indicator."""

    status: Literal["ok"]
