"""Call OpenAI's Responses API and reduce provider JSON to generated text."""

from typing import Any

import httpx


class OpenAIResponsesError(Exception):
    """Raised when the OpenAI Responses API cannot generate an answer."""


class OpenAIResponsesConfigurationError(OpenAIResponsesError):
    """Raised when the OpenAI integration is not configured."""


class OpenAIResponsesAdapter:
    """Small async client for server-side Responses API text generation."""

    def __init__(
        self,
        api_key: str | None,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Configure authentication, model selection, timeout, and test transport."""

        self.api_key = api_key.strip() if api_key else None
        self.model = model.strip()
        self.base_url = f"{base_url.rstrip('/')}/"
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    @property
    def is_configured(self) -> bool:
        """Report whether a non-placeholder key and model are available."""

        return _is_usable_key(self.api_key) and bool(self.model)

    async def generate_answer(
        self, messages: list[dict[str, str]], instructions: str
    ) -> str:
        """Generate one stateless text answer from conversation input and instructions."""

        if not self.is_configured:
            raise OpenAIResponsesConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    "responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "instructions": instructions,
                        "input": messages,
                        "max_output_tokens": 900,
                        "store": False,
                        "text": {"verbosity": "medium"},
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OpenAIResponsesError("OpenAI response generation failed.") from exc

        output_text = _extract_output_text(payload)
        if not output_text:
            raise OpenAIResponsesError("OpenAI returned an empty response.")
        return output_text


def _is_usable_key(value: str | None) -> bool:
    """Treat missing and documented sample values as unconfigured credentials."""

    if not value:
        return False
    normalized = value.strip().casefold()
    return normalized not in {
        "dummy",
        "placeholder",
        "replace_with_openai_api_key",
    }


def _extract_output_text(payload: Any) -> str | None:
    """Extract direct or nested text while tolerating valid Responses API shapes."""

    if not isinstance(payload, dict):
        return None
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    output = payload.get("output")
    if not isinstance(output, list):
        return None
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "output_text":
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
    return "\n".join(chunks) or None
