import hashlib

from app.config import get_settings
from app.utils.chunking import TextChunk, chunk_text_by_tokens
from app.utils.text_processing import extract_text_from_file

settings = get_settings()


def build_document_chunks(file_path: str) -> tuple[str, list[TextChunk], str]:
    parsed_text = extract_text_from_file(file_path)
    if not parsed_text.strip():
        raise ValueError("No parseable text extracted from document")

    chunks = chunk_text_by_tokens(
        parsed_text,
        chunk_size_tokens=settings.chunk_size_tokens,
        chunk_overlap_tokens=settings.chunk_overlap_tokens,
        model_name=settings.embedding_model_name,
    )
    content_hash = hashlib.sha256(parsed_text.encode("utf-8")).hexdigest()
    return parsed_text, chunks, content_hash
