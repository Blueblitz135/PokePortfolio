import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
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
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    existing_uploads = set(settings.upload_dir.iterdir())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    for uploaded_path in set(settings.upload_dir.iterdir()) - existing_uploads:
        if uploaded_path.is_file():
            uploaded_path.unlink()


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
    assert body["images"] == []
    assert body["primary_image_url"] == "/static/placeholders/asset.svg"
    placeholder_response = client.get(body["primary_image_url"])
    assert placeholder_response.status_code == 200
    assert placeholder_response.headers["content-type"].startswith("image/svg+xml")
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


SEALED_PRODUCT_TYPES = [
    "booster_box",
    "booster_pack",
    "elite_trainer_box",
    "booster_bundle",
    "tin",
    "collection_box",
    "other",
]


@pytest.mark.parametrize("sealed_product_type", SEALED_PRODUCT_TYPES)
def test_create_sealed_product(sealed_product_type: str) -> None:
    product_name = sealed_product_type.replace("_", " ").title()
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "sealed_product",
            "display_name": product_name,
            "sealed_product_metadata": {
                "product_name": product_name,
                "set_name": "Evolving Skies",
                "year": 2021,
                "sealed_product_type": sealed_product_type,
                "is_pokemon_center_exclusive": (
                    sealed_product_type == "elite_trainer_box"
                ),
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sealed_product_metadata"]["sealed_product_type"] == (
        sealed_product_type
    )
    assert "pack_count" not in body["sealed_product_metadata"]
    assert "quantity" not in body
    assert body["primary_image_url"] == "/static/placeholders/asset.svg"


def test_create_sealed_product_rejects_unknown_product_type() -> None:
    response = client.post(
        "/api/assets",
        json={
            "asset_type": "sealed_product",
            "display_name": "Mystery Product",
            "sealed_product_metadata": {
                "product_name": "Mystery Product",
                "sealed_product_type": "mystery_product",
            },
        },
    )

    assert response.status_code == 422


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


ASSET_IMAGE_PAYLOADS = {
    "raw_card": {
        "asset_type": "raw_card",
        "display_name": "Pikachu Raw",
        "card_metadata": {
            "name": "Pikachu",
            "set_name": "Base Set",
            "card_number": "58",
            "set_total": "102",
            "image_url": "https://assets.example.test/pikachu.png",
        },
        "raw_details": {"condition": "NM"},
    },
    "graded_card": {
        "asset_type": "graded_card",
        "display_name": "Pikachu PSA 10",
        "card_metadata": {
            "name": "Pikachu",
            "set_name": "Base Set",
            "card_number": "58",
            "set_total": "102",
        },
        "graded_details": {"grading_company": "PSA", "grade": "10"},
    },
    "sealed_product": {
        "asset_type": "sealed_product",
        "display_name": "Base Set Booster Pack",
        "sealed_product_metadata": {
            "product_name": "Base Set Booster Pack",
            "sealed_product_type": "booster_pack",
        },
    },
}

IMAGE_CONTENT = {
    "jpg": (b"\xff\xd8\xff\xe0test", "image/jpeg"),
    "jpeg": (b"\xff\xd8\xff\xe0test", "image/jpeg"),
    "png": (b"\x89PNG\r\n\x1a\ntest", "image/png"),
    "webp": (b"RIFF\x04\x00\x00\x00WEBP", "image/webp"),
}


def _create_image_test_asset(asset_type: str = "raw_card") -> int:
    response = client.post("/api/assets", json=ASSET_IMAGE_PAYLOADS[asset_type])
    assert response.status_code == 201
    return response.json()["id"]


def test_card_metadata_image_is_used_without_creating_asset_image() -> None:
    asset_id = _create_image_test_asset()

    detail = client.get(f"/api/assets/{asset_id}").json()

    assert detail["primary_image_url"] == (
        ASSET_IMAGE_PAYLOADS["raw_card"]["card_metadata"]["image_url"]
    )
    assert detail["images"] == []


@pytest.mark.parametrize("asset_type", ASSET_IMAGE_PAYLOADS)
def test_upload_image_for_each_asset_type(asset_type: str) -> None:
    asset_id = _create_image_test_asset(asset_type)
    content, content_type = IMAGE_CONTENT["png"]

    response = client.post(
        f"/api/assets/{asset_id}/images",
        files={"file": ("../../card.png", content, content_type)},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["asset_id"] == asset_id
    assert body["image_type"] == "uploaded"
    assert body["is_primary"] is True
    assert body["url_or_path"].startswith("/uploads/")
    assert ".." not in body["url_or_path"]

    served_image = client.get(body["url_or_path"])
    assert served_image.status_code == 200
    assert served_image.content == content

    detail = client.get(f"/api/assets/{asset_id}").json()
    assert detail["primary_image_url"] == body["url_or_path"]
    assert detail["images"] == [body]

    listed_asset = client.get("/api/assets").json()[0]
    assert listed_asset["primary_image_url"] == body["url_or_path"]


@pytest.mark.parametrize("extension", IMAGE_CONTENT)
def test_upload_accepts_supported_image_types(extension: str) -> None:
    asset_id = _create_image_test_asset()
    content, content_type = IMAGE_CONTENT[extension]

    response = client.post(
        f"/api/assets/{asset_id}/images",
        files={"file": (f"card.{extension}", content, content_type)},
    )

    assert response.status_code == 201
    assert response.json()["url_or_path"].endswith(f".{extension}")


def test_new_primary_image_replaces_previous_primary() -> None:
    asset_id = _create_image_test_asset()
    png_content, png_type = IMAGE_CONTENT["png"]
    jpg_content, jpg_type = IMAGE_CONTENT["jpg"]

    first = client.post(
        f"/api/assets/{asset_id}/images",
        files={"file": ("first.png", png_content, png_type)},
    ).json()
    second_response = client.post(
        f"/api/assets/{asset_id}/images",
        data={"is_primary": "true"},
        files={"file": ("second.jpg", jpg_content, jpg_type)},
    )

    assert second_response.status_code == 201
    second = second_response.json()
    images_response = client.get(f"/api/assets/{asset_id}/images")
    assert images_response.status_code == 200
    images = images_response.json()
    assert [image["id"] for image in images] == [first["id"], second["id"]]
    assert [image["is_primary"] for image in images] == [False, True]
    assert client.get(f"/api/assets/{asset_id}").json()[
        "primary_image_url"
    ] == second["url_or_path"]


@pytest.mark.parametrize(
    ("filename", "content", "content_type"),
    [
        ("card.gif", b"GIF89a", "image/gif"),
        ("card.png", b"not a png", "image/png"),
        ("card.png", IMAGE_CONTENT["png"][0], "text/plain"),
    ],
)
def test_upload_rejects_invalid_image_types(
    filename: str, content: bytes, content_type: str
) -> None:
    asset_id = _create_image_test_asset()
    uploads_before = set(settings.upload_dir.iterdir())

    response = client.post(
        f"/api/assets/{asset_id}/images",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 400
    assert client.get(f"/api/assets/{asset_id}/images").json() == []
    assert set(settings.upload_dir.iterdir()) == uploads_before


def test_upload_rejects_images_larger_than_five_mb() -> None:
    asset_id = _create_image_test_asset()
    oversized_content = IMAGE_CONTENT["png"][0] + b"0" * (
        settings.max_upload_size_bytes
    )

    response = client.post(
        f"/api/assets/{asset_id}/images",
        files={"file": ("large.png", oversized_content, "image/png")},
    )

    assert response.status_code == 413
    assert client.get(f"/api/assets/{asset_id}/images").json() == []


def test_upload_requires_existing_asset() -> None:
    content, content_type = IMAGE_CONTENT["png"]
    uploads_before = set(settings.upload_dir.iterdir())

    response = client.post(
        "/api/assets/999/images",
        files={"file": ("card.png", content, content_type)},
    )

    assert response.status_code == 404
    assert set(settings.upload_dir.iterdir()) == uploads_before
