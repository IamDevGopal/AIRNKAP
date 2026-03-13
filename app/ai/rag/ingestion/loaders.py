from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
)
from langchain_core.documents import Document as LangChainDocument


def load_documents(file_path: str) -> list[LangChainDocument]:
    suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

    if suffix == "pdf":
        return PyPDFLoader(file_path).load()
    if suffix == "docx":
        return Docx2txtLoader(file_path).load()
    if suffix in {"txt", "json"}:
        return TextLoader(file_path, encoding="utf-8").load()
    if suffix == "csv":
        return CSVLoader(file_path, encoding="utf-8").load()
    if suffix == "xlsx":
        return UnstructuredExcelLoader(file_path).load()

    raise ValueError(f"Unsupported file extension for LangChain loading: .{suffix}")
