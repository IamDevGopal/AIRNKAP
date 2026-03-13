from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()


def request_embeddings(inputs: list[str]) -> list[dict[str, Any]]:
    if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
        raise ValueError("Azure OpenAI embedding configuration is missing")

    endpoint = settings.azure_openai_endpoint.rstrip("/")
    deployment = settings.azure_openai_embedding_deployment
    url = (
        f"{endpoint}/openai/deployments/{deployment}/embeddings"
        f"?api-version={settings.azure_openai_api_version}"
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": settings.azure_openai_api_key,
    }
    payload = {"input": inputs}

    with httpx.Client(timeout=settings.embedding_request_timeout_seconds) as client:
        response = client.post(url, headers=headers, json=payload)
        if response.status_code >= 500:
            raise RuntimeError(f"Azure OpenAI temporary error: {response.status_code}")
        response.raise_for_status()
        body = response.json()

    data = body.get("data")
    if not isinstance(data, list):
        raise RuntimeError("Invalid embedding response payload: missing data list")
    return data
