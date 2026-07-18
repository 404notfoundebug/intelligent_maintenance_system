from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


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

    vision_api_key: str | None = Field(default=None, alias="VISION_API_KEY")
    vision_base_url: str | None = Field(default=None, alias="VISION_BASE_URL")
    vision_model: str | None = Field(default=None, alias="VISION_MODEL")

    @field_validator("database_url")
    @classmethod
    def validate_local_mysql_url(cls, value: str | None) -> str | None:
        if not value:
            return value

        url = make_url(value)
        if url.drivername != "mysql+pymysql":
            raise ValueError("DATABASE_URL 必须使用 mysql+pymysql 驱动")
        if (url.host or "").lower() not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("DATABASE_URL 必须指向本机 MySQL（localhost 或 127.0.0.1）")
        if not url.database:
            raise ValueError("DATABASE_URL 必须指定数据库名称")
        return value

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
