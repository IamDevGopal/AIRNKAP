from dataclasses import dataclass

from app.ai.vectorstore.retrieval.search import (
    RetrievalScope as VectorstoreRetrievalScope,
    VectorSearchResult,
    search_similar_chunks,
)

RetrievalScope = VectorstoreRetrievalScope


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_text: str
    score: float
    document_id: int | None
    project_id: int | None
    workspace_id: int | None
    chunk_index: int | None
    token_count: int | None
    metadata: dict[str, int | str]


def retrieve_chunks(
    *,
    query_text: str,
    scope: RetrievalScope,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    search_results = search_similar_chunks(query_text=query_text, scope=scope, top_k=top_k)
    return [_map_search_result(result) for result in search_results]


def _map_search_result(result: VectorSearchResult) -> RetrievedChunk:
    metadata = result.metadata
    document_id = _get_int(metadata, "document_id")
    project_id = _get_int(metadata, "project_id")
    workspace_id = _get_int(metadata, "workspace_id")
    chunk_index = _get_int(metadata, "chunk_index")
    token_count = _get_int(metadata, "token_count")

    return RetrievedChunk(
        chunk_text=result.chunk_text,
        score=result.score,
        document_id=document_id,
        project_id=project_id,
        workspace_id=workspace_id,
        chunk_index=chunk_index,
        token_count=token_count,
        metadata=metadata,
    )


def _get_int(metadata: dict[str, int | str], key: str) -> int | None:
    value = metadata.get(key)
    return value if isinstance(value, int) else None
