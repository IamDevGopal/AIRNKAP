from typing import Any, cast


def load_documents(file_path: str) -> list[Any]:
    suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

    try:
        from langchain_community.document_loaders import (
            CSVLoader,
            Docx2txtLoader,
            PyPDFLoader,
            TextLoader,
            UnstructuredExcelLoader,
        )
    except ImportError as exc:
        raise RuntimeError(
            "LangChain document loader dependencies are missing. Install langchain-community and related extras."
        ) from exc

    if suffix == "pdf":
        return cast(list[Any], PyPDFLoader(file_path).load())
    if suffix == "docx":
        return cast(list[Any], Docx2txtLoader(file_path).load())
    if suffix in {"txt", "json"}:
        return cast(list[Any], TextLoader(file_path, encoding="utf-8").load())
    if suffix == "csv":
        return cast(list[Any], CSVLoader(file_path, encoding="utf-8").load())
    if suffix == "xlsx":
        return cast(list[Any], UnstructuredExcelLoader(file_path).load())

    raise ValueError(f"Unsupported file extension for LangChain loading: .{suffix}")
