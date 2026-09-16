from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chat import PortfolioChatResponse
from app.services import portfolio_chat as portfolio_chat_service


client = TestClient(app)


def test_portfolio_chat_endpoint_returns_grounded_answer(monkeypatch) -> None:
    async def fake_answer(db, request):
        assert request.messages[-1].content == "How am I doing?"
        return PortfolioChatResponse(
            message="Raw cards are up based on the available CAD data.",
            generated_at=datetime(2026, 9, 13, tzinfo=timezone.utc),
            providers=[
                {
                    "provider": "JustTCG",
                    "state": "available",
                    "detail": "Matched 1 of 1 raw cards.",
                }
            ],
        )

    monkeypatch.setattr(
        portfolio_chat_service, "answer_portfolio_question", fake_answer
    )

    response = client.post(
        "/api/portfolio-chat",
        json={"messages": [{"role": "user", "content": "How am I doing?"}]},
    )

    assert response.status_code == 200
    assert response.json()["message"].startswith("Raw cards are up")
    assert response.json()["providers"][0]["provider"] == "JustTCG"


def test_portfolio_chat_endpoint_requires_a_final_user_message() -> None:
    response = client.post(
        "/api/portfolio-chat",
        json={"messages": [{"role": "assistant", "content": "Previous answer"}]},
    )

    assert response.status_code == 422
