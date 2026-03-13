from typing import Any

from pydantic import SecretStr

from app.config import get_settings

settings = get_settings()


def get_embeddings_client() -> Any:
    try:
        from langchain_openai import AzureOpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "LangChain embeddings dependencies are missing. Install langchain-openai first."
        ) from exc

    return AzureOpenAIEmbeddings(
        model=settings.embedding_model_name,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=SecretStr(settings.azure_openai_api_key),
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_embedding_deployment,
        chunk_size=settings.embedding_batch_size,
        timeout=settings.embedding_request_timeout_seconds,
        max_retries=settings.embedding_max_retries,
    )
