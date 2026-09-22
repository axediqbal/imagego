from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application and pipeline configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ai_provider: Literal["pollinations", "mock", "openai", "stability"] = "pollinations"
    openai_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_bucket: str = "artwork-images"
    supabase_table: str = "artworks"
    host: str = "127.0.0.1"
    port: int = 8000
    max_retries: int = 3
    output_dir: Path = Path("outputs")
    simulate_corruption_test: bool = False

    def get_output_path(self) -> Path:
        """Ensure outputs directory exists and return absolute path."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir.resolve()


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton instance of application settings."""
    settings = Settings()
    settings.get_output_path()
    return settings
