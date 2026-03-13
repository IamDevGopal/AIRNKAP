from dataclasses import dataclass

from app.ai.rag.retrieval.retriever import RetrievedChunk


@dataclass(frozen=True, slots=True)
class ContextSource:
    document_id: int | None
    project_id: int | None
    workspace_id: int | None
    chunk_index: int | None
    score: float


@dataclass(frozen=True, slots=True)
class ContextBundle:
    context_text: str
    sources: list[ContextSource]
    chunk_count: int


def build_context_bundle(
    chunks: list[RetrievedChunk],
    *,
    max_chunks: int = 5,
) -> ContextBundle:
    unique_chunks = _deduplicate_chunks(chunks)[:max_chunks]
    context_parts: list[str] = []
    sources: list[ContextSource] = []

    for chunk in unique_chunks:
        context_parts.append(chunk.chunk_text.strip())
        sources.append(
            ContextSource(
                document_id=chunk.document_id,
                project_id=chunk.project_id,
                workspace_id=chunk.workspace_id,
                chunk_index=chunk.chunk_index,
                score=chunk.score,
            )
        )

    context_text = "\n\n".join(part for part in context_parts if part)
    return ContextBundle(
        context_text=context_text,
        sources=sources,
        chunk_count=len(unique_chunks),
    )


def _deduplicate_chunks(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    seen_texts: set[str] = set()
    unique_chunks: list[RetrievedChunk] = []

    for chunk in chunks:
        normalized_text = chunk.chunk_text.strip()
        if not normalized_text or normalized_text in seen_texts:
            continue
        seen_texts.add(normalized_text)
        unique_chunks.append(chunk)

    return unique_chunks
