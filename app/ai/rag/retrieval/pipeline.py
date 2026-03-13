from dataclasses import dataclass

from app.ai.rag.retrieval.context_builder import ContextBundle, build_context_bundle
from app.ai.rag.retrieval.retriever import RetrievalScope, RetrievedChunk, retrieve_chunks


@dataclass(frozen=True, slots=True)
class RetrievalRequest:
    query_text: str
    scope: RetrievalScope
    top_k: int = 5
    max_context_chunks: int = 5


@dataclass(frozen=True, slots=True)
class RetrievalResponse:
    chunks: list[RetrievedChunk]
    context: ContextBundle


def run_retrieval_pipeline(request: RetrievalRequest) -> RetrievalResponse:
    chunks = retrieve_chunks(
        query_text=request.query_text,
        scope=request.scope,
        top_k=request.top_k,
    )
    context = build_context_bundle(
        chunks,
        max_chunks=request.max_context_chunks,
    )
    return RetrievalResponse(chunks=chunks, context=context)
