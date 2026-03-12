import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

settings = get_settings()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
        raise ValueError("Azure OpenAI embedding configuration is missing")

    endpoint = settings.azure_openai_endpoint.rstrip("/")
    deployment = settings.azure_openai_embedding_deployment
    url = (
        f"{endpoint}/openai/deployments/{deployment}/embeddings"
        f"?api-version={settings.azure_openai_api_version}"
    )

    all_vectors: list[list[float]] = []
    for batch in _batch_texts(texts, settings.embedding_batch_size):
        all_vectors.extend(_request_embeddings(url=url, batch=batch))
    return all_vectors


@retry(
    stop=stop_after_attempt(settings.embedding_max_retries),
    wait=wait_exponential(multiplier=1, min=1, max=15),
    retry=retry_if_exception_type((httpx.HTTPError, RuntimeError)),
    reraise=True,
)
def _request_embeddings(*, url: str, batch: list[str]) -> list[list[float]]:
    headers = {
        "Content-Type": "application/json",
        "api-key": settings.azure_openai_api_key,
    }
    payload = {"input": batch}

    with httpx.Client(timeout=settings.embedding_request_timeout_seconds) as client:
        response = client.post(url, headers=headers, json=payload)
        if response.status_code >= 500:
            raise RuntimeError(f"Azure OpenAI temporary error: {response.status_code}")
        response.raise_for_status()
        body = response.json()

    data = body.get("data")
    if not isinstance(data, list):
        raise RuntimeError("Invalid embedding response payload: missing data list")

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
