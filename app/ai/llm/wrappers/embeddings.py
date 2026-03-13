from typing import Any

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
        api_key=settings.azure_openai_api_key,
        openai_api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_embedding_deployment,
        chunk_size=settings.embedding_batch_size,
        timeout=settings.embedding_request_timeout_seconds,
        max_retries=settings.embedding_max_retries,
    )


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = get_embeddings_client()
    vectors = embeddings.embed_documents(texts)
    return [[float(value) for value in vector] for vector in vectors]
