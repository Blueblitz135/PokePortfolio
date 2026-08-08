from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Pokemon Portfolio API"
    database_url: str = "sqlite:///./pokemon_portfolio.db"
    upload_dir: Path = BACKEND_DIR / "uploads"
    max_upload_size_bytes: int = 5 * 1024 * 1024
    tcgdex_base_url: str = "https://api.tcgdex.net/v2/en"
    tcgdex_timeout_seconds: float = 10.0
    tcgdex_search_limit: int = 20
    justtcg_api_key: str | None = None
    justtcg_base_url: str = "https://api.justtcg.com/v1"
    justtcg_timeout_seconds: float = 10.0
    justtcg_usd_to_cad_rate: Decimal | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
