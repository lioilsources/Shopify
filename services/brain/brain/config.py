from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required, no fallback: a missing DATABASE_URL must fail at start.
    database_url: str

    # Aliases routed by the AiStack gateway (LiteLLM).
    llm_base_url: str = ""
    llm_model: str = "shop"
    llm_api_key: str = "not-needed"

    embeddings_base_url: str = ""
    embeddings_model: str = "shop-embed"
    # Falls back to llm_api_key (same gateway).
    embeddings_api_key: str = ""
    embedding_dim: int = 1024
    # Seconds; a short timeout keeps chat usable when SPARK is busy.
    embeddings_timeout: float = 5.0

    # Shared secret for /ingest and /admin/*; held only by the web BFF on the server.
    admin_token: str = ""

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_base_url)

    @property
    def embeddings_enabled(self) -> bool:
        return bool(self.embeddings_base_url)

    @property
    def embedding_model_name(self) -> str:
        """Name stored with each vector; mock vectors never mix with real ones."""
        return self.embeddings_model if self.embeddings_enabled else "mock"


settings = Settings()
