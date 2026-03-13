import hashlib

from app.ai.rag.ingestion.loaders import load_documents
from app.ai.rag.ingestion.splitters import TextChunk, split_documents
from app.config import get_settings

settings = get_settings()


def build_document_chunks(file_path: str) -> tuple[str, list[TextChunk], str]:
    documents = load_documents(file_path)
    parsed_text = "\n\n".join(
        getattr(document, "page_content", "").strip()
        for document in documents
        if getattr(document, "page_content", "").strip()
    )
    if not parsed_text.strip():
        raise ValueError("No parseable text extracted from document")

    chunks = split_documents(documents)
    content_hash = hashlib.sha256(parsed_text.encode("utf-8")).hexdigest()
    return parsed_text, chunks, content_hash
