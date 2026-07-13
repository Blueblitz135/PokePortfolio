import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


def test_create_raw_card() -> None:
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "raw_card",
            "display_name": "Umbreon VMAX - Evolving Skies - Raw NM",
            "user_note": "Long-term hold",
            "card_metadata": {
                "name": "Umbreon VMAX",
                "set_name": "Evolving Skies",
                "year": 2021,
                "card_number": "215",
                "set_total": "203",
            },
            "raw_details": {"condition": "NM"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["card_metadata"]["card_number"] == "215"
    assert body["card_metadata"]["set_total"] == "203"
    assert body["raw_details"]["condition"] == "NM"
    assert "quantity" not in body
    assert body["purchase_lots"] == []
    assert body["summary"] == {
        "total_quantity": 0,
        "total_cost": "0",
        "average_cost_per_unit": None,
        "market_price_per_unit": None,
        "total_market_value": None,
        "profit_loss": None,
        "roi_percent": None,
    }


def test_create_graded_card() -> None:
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "graded_card",
            "display_name": "Umbreon VMAX - Evolving Skies - PSA 10",
            "card_metadata": {
                "name": "Umbreon VMAX",
                "set_name": "Evolving Skies",
                "card_number": "215",
                "set_total": "203",
            },
            "graded_details": {"grading_company": "PSA", "grade": "10"},
        },
    )

    assert response.status_code == 201
    assert response.json()["graded_details"] == {
        "grading_company": "PSA",
        "grade": "10.0",
        "cert_number": None,
    }


def test_create_sealed_product() -> None:
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "sealed_product",
            "display_name": "Evolving Skies Booster Box",
            "sealed_product_metadata": {
                "product_name": "Evolving Skies Booster Box",
                "set_name": "Evolving Skies",
                "year": 2021,
                "sealed_product_type": "booster_box",
            },
        },
    )

    assert response.status_code == 201
    assert response.json()["sealed_product_metadata"]["sealed_product_type"] == (
        "booster_box"
    )


def test_list_get_update_and_delete_asset() -> None:
    created = client.post(
        "/api/assets",
        json={
            "asset_type": "sealed_product",
            "display_name": "Evolving Skies Booster Box",
            "sealed_product_metadata": {
                "product_name": "Evolving Skies Booster Box",
                "sealed_product_type": "booster_box",
            },
        },
    ).json()
    asset_id = created["id"]

    list_response = client.get("/api/assets")
    assert list_response.status_code == 200
    assert [asset["id"] for asset in list_response.json()] == [asset_id]

    get_response = client.get(f"/api/assets/{asset_id}")
    assert get_response.status_code == 200

    update_response = client.patch(
        f"/api/assets/{asset_id}",
        json={"display_name": "Updated Booster Box", "user_note": "Keep sealed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "Updated Booster Box"
    assert update_response.json()["user_note"] == "Keep sealed"

    delete_response = client.delete(f"/api/assets/{asset_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/assets/{asset_id}").status_code == 404


def test_create_rejects_metadata_for_wrong_asset_type() -> None:
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "raw_card",
            "display_name": "Invalid raw card",
            "sealed_product_metadata": {
                "product_name": "Booster Box",
                "sealed_product_type": "booster_box",
            },
        },
    )

    assert response.status_code == 422


def test_create_update_and_delete_purchase_lots() -> None:
    asset_id = client.post(
        "/api/assets",
        json={
            "asset_type": "sealed_product",
            "display_name": "Evolving Skies Booster Box",
            "sealed_product_metadata": {
                "product_name": "Evolving Skies Booster Box",
                "sealed_product_type": "booster_box",
            },
        },
    ).json()["id"]

    first_lot = client.post(
        f"/api/assets/{asset_id}/purchase-lots",
        json={
            "purchase_date": "2025-08-01",
            "quantity": 1,
            "purchase_price_per_unit": "750.00",
        },
    )
    second_lot = client.post(
        f"/api/assets/{asset_id}/purchase-lots",
        json={
            "purchase_date": "2026-02-15",
            "quantity": 2,
            "purchase_price_per_unit": "900.00",
            "currency": "cad",
        },
    )

    assert first_lot.status_code == 201
    assert second_lot.status_code == 201
    assert second_lot.json()["currency"] == "CAD"

    detail = client.get(f"/api/assets/{asset_id}").json()
    assert len(detail["purchase_lots"]) == 2
    assert detail["summary"]["total_quantity"] == 3
    assert detail["summary"]["total_cost"] == "2550.00"
    assert detail["summary"]["average_cost_per_unit"] == "850.00"
    assert detail["summary"]["market_price_per_unit"] is None

    lot_id = second_lot.json()["id"]
    update_response = client.patch(
        f"/api/purchase-lots/{lot_id}",
        json={"quantity": 3, "purchase_price_per_unit": "800.00"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["quantity"] == 3

    updated_detail = client.get(f"/api/assets/{asset_id}").json()
    assert updated_detail["summary"]["total_quantity"] == 4
    assert updated_detail["summary"]["total_cost"] == "3150.00"

    delete_response = client.delete(f"/api/purchase-lots/{lot_id}")

    assert delete_response.status_code == 204
    final_detail = client.get(f"/api/assets/{asset_id}").json()
    assert final_detail["summary"]["total_quantity"] == 1
    assert len(final_detail["purchase_lots"]) == 1


def test_purchase_lot_requires_existing_asset() -> None:
    response = client.post(
        "/api/assets/999/purchase-lots",
        json={
            "purchase_date": "2025-08-01",
            "quantity": 1,
            "purchase_price_per_unit": "750.00",
        },
    )

    assert response.status_code == 404
