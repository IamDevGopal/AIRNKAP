from dataclasses import dataclass

from langchain_core.documents import Document as LangChainDocument

from app.config import get_settings

settings = get_settings()


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_index: int
    chunk_text: str
    token_count: int


def split_documents(documents: list[LangChainDocument]) -> list[TextChunk]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError as exc:
        raise RuntimeError(
            "LangChain text splitter dependency is missing. Install langchain-text-splitters."
        ) from exc

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=settings.embedding_model_name,
        chunk_size=settings.chunk_size_tokens,
        chunk_overlap=settings.chunk_overlap_tokens,
    )
    split_docs = splitter.split_documents(documents)

    chunks: list[TextChunk] = []
    for index, document in enumerate(split_docs):
        page_content = getattr(document, "page_content", "").strip()
        if not page_content:
            continue
        chunks.append(
            TextChunk(
                chunk_index=index,
                chunk_text=page_content,
                token_count=len(page_content.split()),
            )
        )
    return chunks
