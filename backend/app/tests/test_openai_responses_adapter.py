import asyncio

import httpx
import pytest

from app.adapters.openai_responses import (
    MAX_OUTPUT_TOKENS,
    OpenAIResponsesAdapter,
    OpenAIResponsesConfigurationError,
    OpenAIResponsesError,
)


def test_adapter_calls_responses_api_without_storing_the_conversation() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        assert request.headers["Authorization"] == "Bearer test-key"
        body = __import__("json").loads(request.content)
        assert body["model"] == "gpt-5-mini"
        assert body["instructions"] == "Detailed system context"
        assert body["input"] == [{"role": "user", "content": "How am I doing?"}]
        assert body["max_output_tokens"] == MAX_OUTPUT_TOKENS
        assert body["reasoning"] == {"effort": "low"}
        assert body["text"] == {"verbosity": "low"}
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


def test_adapter_identifies_a_response_that_exhausted_its_token_budget() -> None:
    adapter = OpenAIResponsesAdapter(
        api_key="test-key",
        model="gpt-5-mini",
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200,
                json={
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "output": [{"type": "reasoning", "content": []}],
                },
            )
        ),
    )

    with pytest.raises(OpenAIResponsesError, match="output token budget"):
        asyncio.run(adapter.generate_answer([], "context"))
