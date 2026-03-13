from dataclasses import dataclass
from typing import Literal

from langchain_core.documents import Document as LangChainDocument
from langchain_pinecone import PineconeVectorStore

from app.ai.llm.wrappers.embeddings import get_embeddings_client
from app.ai.vectorstore.clients.pinecone_client import get_pinecone_index
from app.config import get_settings

settings = get_settings()


@dataclass(frozen=True, slots=True)
class RetrievalScope:
    scope_type: Literal["document", "project", "workspace"]
    scope_id: int


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_text: str
    score: float
    metadata: dict[str, int | str]


def build_scope_filter(scope: RetrievalScope) -> dict[str, int]:
    if scope.scope_type == "document":
        return {"document_id": scope.scope_id}
    if scope.scope_type == "project":
        return {"project_id": scope.scope_id}
    return {"workspace_id": scope.scope_id}


def search_similar_chunks(
    *,
    query_text: str,
    scope: RetrievalScope,
    top_k: int = 5,
) -> list[VectorSearchResult]:
    normalized_query = query_text.strip()
    if not normalized_query:
        return []
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    vector_store = PineconeVectorStore(
        index=get_pinecone_index(),
        embedding=get_embeddings_client(),
        namespace=settings.pinecone_namespace,
    )
    results = vector_store.similarity_search_with_score(
        query=normalized_query,
        k=top_k,
        filter=build_scope_filter(scope),
        namespace=settings.pinecone_namespace,
    )
    return [_map_search_result(document, score) for document, score in results]


def _map_search_result(document: LangChainDocument, score: float) -> VectorSearchResult:
    metadata = _normalize_metadata(document.metadata)
    return VectorSearchResult(
        chunk_text=document.page_content,
        score=float(score),
        metadata=metadata,
    )


def _normalize_metadata(raw_metadata: dict[str, object]) -> dict[str, int | str]:
    normalized_metadata: dict[str, int | str] = {}

    for key, value in raw_metadata.items():
        if isinstance(value, bool):
            normalized_metadata[key] = str(value)
        elif isinstance(value, int | str):
            normalized_metadata[key] = value
        elif value is not None:
            normalized_metadata[key] = str(value)

    return normalized_metadata
