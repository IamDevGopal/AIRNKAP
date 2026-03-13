from collections.abc import Iterable
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.models.document_model import Document
from app.utils.chunking import TextChunk
from app.vectorstore.vector_client import get_pinecone_index

settings = get_settings()


def upsert_document_vectors(
    *,
    document: Document,
    chunks: list[TextChunk],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")
    if not chunks:
        return

    vectors = []
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        vectors.append(
            {
                "id": _build_vector_id(document_id=document.id, chunk_index=chunk.chunk_index),
                "values": embedding,
                "metadata": {
                    "document_id": document.id,
                    "project_id": document.project_id,
                    "workspace_id": document.workspace_id,
                    "owner_id": document.owner_id,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                },
            }
        )

    index = get_pinecone_index()
    for batch in _batch_items(vectors, settings.pinecone_upsert_batch_size):
        _upsert_batch(index=index, vectors=batch)


@retry(
    stop=stop_after_attempt(settings.embedding_max_retries),
    wait=wait_exponential(multiplier=1, min=1, max=15),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _upsert_batch(*, index: Any, vectors: list[dict[str, Any]]) -> None:
    index.upsert(vectors=vectors, namespace=settings.pinecone_namespace)


def _build_vector_id(*, document_id: int, chunk_index: int) -> str:
    return f"doc-{document_id}-chunk-{chunk_index}"


def _batch_items(items: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    normalized_batch_size = max(1, batch_size)
    for index in range(0, len(items), normalized_batch_size):
        yield items[index : index + normalized_batch_size]
