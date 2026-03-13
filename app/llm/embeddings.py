import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.llm.azure_openai_client import request_embeddings

settings = get_settings()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    all_vectors: list[list[float]] = []
    for batch in _batch_texts(texts, settings.embedding_batch_size):
        all_vectors.extend(_request_embeddings(batch=batch))
    return all_vectors


@retry(
    stop=stop_after_attempt(settings.embedding_max_retries),
    wait=wait_exponential(multiplier=1, min=1, max=15),
    retry=retry_if_exception_type((httpx.HTTPError, RuntimeError)),
    reraise=True,
)
def _request_embeddings(*, batch: list[str]) -> list[list[float]]:
    data = request_embeddings(batch)

    sorted_rows = sorted(data, key=lambda item: int(item["index"]))
    vectors: list[list[float]] = []
    for row in sorted_rows:
        embedding = row.get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("Invalid embedding response row: embedding missing")
        vectors.append([float(value) for value in embedding])

    if len(vectors) != len(batch):
        raise RuntimeError("Embedding response size mismatch")
    return vectors


def _batch_texts(texts: list[str], batch_size: int) -> list[list[str]]:
    normalized_batch_size = max(1, batch_size)
    return [
        texts[index : index + normalized_batch_size]
        for index in range(0, len(texts), normalized_batch_size)
    ]
