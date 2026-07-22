from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://chatshop:chatshop@localhost:5432/chatshop"

    llm_base_url: str = ""
    llm_model: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    llm_api_key: str = "not-needed"

    embeddings_base_url: str = ""
    embeddings_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_base_url)

    @property
    def embeddings_enabled(self) -> bool:
        return bool(self.embeddings_base_url)


settings = Settings()
