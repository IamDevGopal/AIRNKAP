from typing import Any

from pinecone import Pinecone  # type: ignore[import-untyped]

from app.config import get_settings

settings = get_settings()


def get_pinecone_index() -> Any:
    if not settings.pinecone_api_key:
        raise ValueError("Pinecone API key is missing")
    client = Pinecone(api_key=settings.pinecone_api_key)
    return client.Index(settings.pinecone_index_name)
