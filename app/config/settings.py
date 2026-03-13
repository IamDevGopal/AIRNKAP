from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
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
    embedding_provider: Literal["openai", "azure_openai"] = Field(
        default="openai",
        alias="EMBEDDING_PROVIDER",
    )
    llm_provider: Literal["openai", "azure_openai"] = Field(
        default="openai",
        alias="LLM_PROVIDER",
    )
    trusted_hosts: list[str] = Field(default=["localhost", "127.0.0.1"], alias="TRUSTED_HOSTS")

    # Database
    database_url: str = Field(default="sqlite:///./data/sqlite/app.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # Queue / Worker
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_RESULT_BACKEND",
    )
    celery_ingestion_queue: str = Field(
        default="document_ingestion",
        alias="CELERY_INGESTION_QUEUE",
    )
    celery_ingestion_max_retries: int = Field(default=3, alias="CELERY_INGESTION_MAX_RETRIES")
    celery_ingestion_retry_delay_seconds: int = Field(
        default=30,
        alias="CELERY_INGESTION_RETRY_DELAY_SECONDS",
    )

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

    # Upload / Parsing
    upload_max_file_size_mb: int = Field(default=25, alias="UPLOAD_MAX_FILE_SIZE_MB")
    upload_allowed_extensions: list[str] = Field(
        default=["pdf", "docx", "txt", "json", "csv", "xlsx"],
        alias="UPLOAD_ALLOWED_EXTENSIONS",
    )
    upload_allowed_mime_types: list[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/json",
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ],
        alias="UPLOAD_ALLOWED_MIME_TYPES",
    )

    # Chunking / Embeddings
    chunk_size_tokens: int = Field(default=800, alias="CHUNK_SIZE_TOKENS")
    chunk_overlap_tokens: int = Field(default=120, alias="CHUNK_OVERLAP_TOKENS")
    embedding_model_name: str = Field(
        default="text-embedding-3-large",
        alias="EMBEDDING_MODEL_NAME",
    )
    embedding_model_version: str = Field(default="v1", alias="EMBEDDING_MODEL_VERSION")
    chat_model_name: str = Field(default="gpt-4o-mini", alias="CHAT_MODEL_NAME")
    chat_temperature: float = Field(default=0.1, alias="CHAT_TEMPERATURE")
    chat_request_timeout_seconds: int = Field(default=60, alias="CHAT_REQUEST_TIMEOUT_SECONDS")
    chat_max_retries: int = Field(default=3, alias="CHAT_MAX_RETRIES")
    embedding_batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")
    embedding_request_timeout_seconds: int = Field(
        default=30,
        alias="EMBEDDING_REQUEST_TIMEOUT_SECONDS",
    )
    embedding_max_retries: int = Field(default=3, alias="EMBEDDING_MAX_RETRIES")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    azure_openai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        alias="AZURE_OPENAI_API_VERSION",
    )
    azure_openai_embedding_deployment: str = Field(
        default="text-embedding-3-large",
        alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
    )
    azure_openai_chat_deployment: str = Field(
        default="gpt-4o-mini",
        alias="AZURE_OPENAI_CHAT_DEPLOYMENT",
    )

    # Vector Store (Pinecone)
    pinecone_api_key: str = Field(
        default="",
        alias="PINECONE_API_KEY",
        validation_alias=AliasChoices("PINECONE_API_KEY", "PINECODE_DB_API_KEY"),
    )
    pinecone_index_name: str = Field(default="airnkap-docs", alias="PINECONE_INDEX_NAME")
    pinecone_namespace: str = Field(default="default", alias="PINECONE_NAMESPACE")
    pinecone_environment: str = Field(default="us-east-1", alias="PINECONE_ENVIRONMENT")
    pinecone_upsert_batch_size: int = Field(default=100, alias="PINECONE_UPSERT_BATCH_SIZE")

    @field_validator(
        "trusted_hosts",
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        "upload_allowed_extensions",
        "upload_allowed_mime_types",
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

    def safe_summary(self) -> dict[str, str | bool | int | float]:
        # Keep startup logs safe by excluding sensitive values.
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "app_debug": self.app_debug,
            "app_host": self.app_host,
            "app_port": self.app_port,
            "app_log_level": self.app_log_level,
            "embedding_provider": self.embedding_provider,
            "llm_provider": self.llm_provider,
            "database_echo": self.database_echo,
            "redis_url": self.redis_url,
            "celery_broker_url": self.celery_broker_url,
            "celery_result_backend": self.celery_result_backend,
            "celery_ingestion_queue": self.celery_ingestion_queue,
            "jwt_algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window_seconds": self.rate_limit_window_seconds,
            "upload_max_file_size_mb": self.upload_max_file_size_mb,
            "chunk_size_tokens": self.chunk_size_tokens,
            "chunk_overlap_tokens": self.chunk_overlap_tokens,
            "embedding_model_name": self.embedding_model_name,
            "embedding_model_version": self.embedding_model_version,
            "chat_model_name": self.chat_model_name,
            "chat_temperature": self.chat_temperature,
            "chat_request_timeout_seconds": self.chat_request_timeout_seconds,
            "chat_max_retries": self.chat_max_retries,
            "embedding_batch_size": self.embedding_batch_size,
            "embedding_request_timeout_seconds": self.embedding_request_timeout_seconds,
            "embedding_max_retries": self.embedding_max_retries,
            "openai_base_url": self.openai_base_url,
            "azure_openai_endpoint": self.azure_openai_endpoint,
            "azure_openai_api_version": self.azure_openai_api_version,
            "azure_openai_embedding_deployment": self.azure_openai_embedding_deployment,
            "azure_openai_chat_deployment": self.azure_openai_chat_deployment,
            "pinecone_index_name": self.pinecone_index_name,
            "pinecone_namespace": self.pinecone_namespace,
            "pinecone_environment": self.pinecone_environment,
            "pinecone_upsert_batch_size": self.pinecone_upsert_batch_size,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
