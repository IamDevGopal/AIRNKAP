from app.ai.rag.ingestion.pipeline import build_document_chunks
from app.ai.rag.ingestion.splitters import TextChunk
from app.ai.rag.retrieval.pipeline import (
    RetrievalRequest,
    RetrievalResponse,
    run_retrieval_pipeline as _run_retrieval_pipeline,
)


def run_ingestion_pipeline(file_path: str) -> tuple[str, list[TextChunk], str]:
    return build_document_chunks(file_path)


def run_retrieval_pipeline(request: RetrievalRequest) -> RetrievalResponse:
    return _run_retrieval_pipeline(request)
