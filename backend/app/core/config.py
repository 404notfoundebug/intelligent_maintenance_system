from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="智能电梯扶梯维保系统", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    secret_key: str = Field(default="please-change-this-secret-key", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")

    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
