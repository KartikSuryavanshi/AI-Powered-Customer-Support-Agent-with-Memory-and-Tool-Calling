from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Support Copilot API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    mem0_api_key: str | None = Field(default=None, alias="MEM0_API_KEY")

    chroma_persist_dir: str = Field(default="./chroma", alias="CHROMA_PERSIST_DIR")
    sqlite_db_path: str = Field(default="./support_copilot.db", alias="SQLITE_DB_PATH")
    knowledge_base_dir: str = Field(default="./data/knowledge_base", alias="KNOWLEDGE_BASE_DIR")

    streamlit_api_base_url: str = Field(default="http://localhost:8000", alias="STREAMLIT_API_BASE_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.knowledge_base_dir).mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
