import asyncio

import httpx
import pytest

from app.adapters.openai_responses import (
    OpenAIResponsesAdapter,
    OpenAIResponsesConfigurationError,
)


def test_adapter_calls_responses_api_without_storing_the_conversation() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        assert request.headers["Authorization"] == "Bearer test-key"
        body = __import__("json").loads(request.content)
        assert body["model"] == "gpt-5-mini"
        assert body["instructions"] == "Detailed system context"
        assert body["input"] == [{"role": "user", "content": "How am I doing?"}]
        assert body["store"] is False
        return httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "Raw cards are up."}
                        ],
                    }
                ]
            },
        )

    adapter = OpenAIResponsesAdapter(
        api_key="test-key",
        model="gpt-5-mini",
        transport=httpx.MockTransport(handle_request),
    )

    answer = asyncio.run(
        adapter.generate_answer(
            [{"role": "user", "content": "How am I doing?"}],
            "Detailed system context",
        )
    )

    assert answer == "Raw cards are up."


def test_adapter_rejects_the_documented_placeholder_key() -> None:
    adapter = OpenAIResponsesAdapter(
        api_key="replace_with_openai_api_key", model="gpt-5-mini"
    )

    with pytest.raises(OpenAIResponsesConfigurationError):
        asyncio.run(adapter.generate_answer([], "context"))
