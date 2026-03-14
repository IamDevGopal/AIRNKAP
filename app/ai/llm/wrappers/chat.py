from collections.abc import Iterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessageChunk, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import SecretStr

from app.config import get_settings

settings = get_settings()


def get_chat_client() -> BaseChatModel:
    if settings.llm_provider == "openai":
        return ChatOpenAI(
            model=settings.chat_model_name,
            api_key=SecretStr(settings.openai_api_key),
            base_url=settings.openai_base_url,
            temperature=settings.chat_temperature,
            timeout=settings.chat_request_timeout_seconds,
            max_retries=settings.chat_max_retries,
        )

    return AzureChatOpenAI(
        model=settings.chat_model_name,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=SecretStr(settings.azure_openai_api_key),
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_chat_deployment,
        temperature=settings.chat_temperature,
        timeout=settings.chat_request_timeout_seconds,
        max_retries=settings.chat_max_retries,
    )


def generate_grounded_answer(
    *,
    query_text: str,
    context_text: str,
    chat_history: list[tuple[str, str]] | None = None,
) -> str:
    chat_model = get_chat_client()
    messages = _build_grounded_messages(
        query_text=query_text,
        context_text=context_text,
        chat_history=chat_history,
    )
    response = chat_model.invoke(messages)

    if isinstance(response.content, str):
        return response.content.strip()

    return str(response.content).strip()


def generate_contextual_response(
    *,
    system_instruction: str,
    user_instruction: str,
    context_text: str,
    response_instruction: str = "Return a concise grounded answer.",
    chat_history: list[tuple[str, str]] | None = None,
) -> str:
    chat_model = get_chat_client()
    messages = _build_messages(
        system_instruction=system_instruction,
        user_instruction=user_instruction,
        context_text=context_text,
        response_instruction=response_instruction,
        chat_history=chat_history,
    )
    response = chat_model.invoke(messages)
    if isinstance(response.content, str):
        return response.content.strip()
    return str(response.content).strip()


def stream_grounded_answer(
    *,
    query_text: str,
    context_text: str,
    chat_history: list[tuple[str, str]] | None = None,
) -> Iterator[str]:
    chat_model = get_chat_client()
    messages = _build_messages(
        system_instruction=(
            "You answer questions only using the provided context. "
            "If the context is insufficient, clearly say that the answer "
            "is not available in the retrieved project knowledge."
        ),
        user_instruction=f"Question:\n{query_text}",
        context_text=context_text,
        response_instruction="Return a concise grounded answer.",
        chat_history=chat_history,
    )

    for chunk in chat_model.stream(messages):
        text = _extract_chunk_text(chunk)
        if text:
            yield text


def _build_grounded_messages(
    *,
    query_text: str,
    context_text: str,
    chat_history: list[tuple[str, str]] | None,
) -> list[SystemMessage | HumanMessage | AIMessage]:
    return _build_messages(
        system_instruction=(
            "You answer questions only using the provided context. "
            "If the context is insufficient, clearly say that the answer "
            "is not available in the retrieved project knowledge."
        ),
        user_instruction=f"Question:\n{query_text}",
        context_text=context_text,
        response_instruction="Return a concise grounded answer.",
        chat_history=chat_history,
    )


def _build_messages(
    *,
    system_instruction: str,
    user_instruction: str,
    context_text: str,
    response_instruction: str,
    chat_history: list[tuple[str, str]] | None,
) -> list[SystemMessage | HumanMessage | AIMessage]:
    messages: list[SystemMessage | HumanMessage | AIMessage] = [
        SystemMessage(content=system_instruction)
    ]
    if chat_history:
        for role, content in chat_history:
            if role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))

    messages.append(
        HumanMessage(
            content=(f"{user_instruction}\n\nContext:\n{context_text}\n\n{response_instruction}")
        )
    )
    return messages


def _extract_chunk_text(chunk: BaseMessageChunk) -> str:
    if isinstance(chunk.content, str):
        return chunk.content
    return "".join(str(item) for item in chunk.content)
