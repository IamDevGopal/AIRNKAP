from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="AIRNKAP", alias="APP_NAME")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        alias="APP_LOG_LEVEL",
    )
    trusted_hosts: list[str] = Field(default=["localhost", "127.0.0.1"], alias="TRUSTED_HOSTS")

    # Database
    database_url: str = Field(default="sqlite:///./data/sqlite/app.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # Security
    secret_key: str = Field(default="change-this-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_allow_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ALLOW_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        alias="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: list[str] = Field(
        default=["Authorization", "Content-Type"],
        alias="CORS_ALLOW_HEADERS",
    )
    rate_limit_requests: int = Field(default=60, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")

    @field_validator(
        "trusted_hosts",
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        mode="before",
    )
    @classmethod
    def _split_comma_values(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def safe_summary(self) -> dict[str, str | bool | int]:
        # Keep startup logs safe by excluding sensitive values.
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "app_debug": self.app_debug,
            "app_host": self.app_host,
            "app_port": self.app_port,
            "app_log_level": self.app_log_level,
            "database_echo": self.database_echo,
            "jwt_algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window_seconds": self.rate_limit_window_seconds,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
