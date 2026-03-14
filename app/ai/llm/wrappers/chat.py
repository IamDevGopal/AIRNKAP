from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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
    messages: list[SystemMessage | HumanMessage | AIMessage] = [
        SystemMessage(
            content=(
                "You answer questions only using the provided context. "
                "If the context is insufficient, clearly say that the answer "
                "is not available in the retrieved project knowledge."
            )
        )
    ]
    if chat_history:
        for role, content in chat_history:
            if role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))

    messages.append(
        HumanMessage(
            content=(
                f"Question:\n{query_text}\n\n"
                f"Context:\n{context_text}\n\n"
                "Return a concise grounded answer."
            )
        )
    )

    response = chat_model.invoke(messages)

    if isinstance(response.content, str):
        return response.content.strip()

    return str(response.content).strip()
