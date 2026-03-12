from dataclasses import dataclass

import tiktoken


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_index: int
    chunk_text: str
    token_count: int


def chunk_text_by_tokens(
    text: str,
    *,
    chunk_size_tokens: int,
    chunk_overlap_tokens: int,
    model_name: str,
) -> list[TextChunk]:
    normalized_text = text.strip()
    if not normalized_text:
        return []
    if chunk_size_tokens <= 0:
        raise ValueError("chunk_size_tokens must be > 0")

    overlap = max(0, chunk_overlap_tokens)
    if overlap >= chunk_size_tokens:
        overlap = chunk_size_tokens - 1

    encoding = _resolve_tokenizer(model_name)
    tokens = encoding.encode(normalized_text)
    if not tokens:
        return []

    step = max(1, chunk_size_tokens - overlap)
    chunks: list[TextChunk] = []
    index = 0

    for start in range(0, len(tokens), step):
        end = min(start + chunk_size_tokens, len(tokens))
        window = tokens[start:end]
        if not window:
            break

        chunk_text = encoding.decode(window).strip()
        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_index=index,
                    chunk_text=chunk_text,
                    token_count=len(window),
                )
            )
            index += 1

        if end >= len(tokens):
            break

    return chunks


def _resolve_tokenizer(model_name: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")
