from langchain_pinecone import PineconeVectorStore

from app.ai.llm.wrappers.embeddings import get_embeddings_client
from app.ai.rag.ingestion.splitters import TextChunk
from app.config import get_settings
from app.models.document_model import Document

settings = get_settings()


def upsert_document_vectors(
    *,
    document: Document,
    chunks: list[TextChunk],
) -> None:
    if not chunks:
        return

    embeddings = get_embeddings_client()
    vector_store = PineconeVectorStore(
        index_name=settings.pinecone_index_name,
        embedding=embeddings,
        namespace=settings.pinecone_namespace,
        pinecone_api_key=settings.pinecone_api_key,
    )
    vector_store.add_texts(
        texts=[chunk.chunk_text for chunk in chunks],
        metadatas=[
            {
                "document_id": document.id,
                "project_id": document.project_id,
                "workspace_id": document.workspace_id,
                "owner_id": document.owner_id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
            }
            for chunk in chunks
        ],
        ids=[f"doc-{document.id}-chunk-{chunk.chunk_index}" for chunk in chunks],
        namespace=settings.pinecone_namespace,
    )
