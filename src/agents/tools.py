"""Shared LangChain tool definitions for agent modules."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever

from src.rag.config import REPO_ROOT
from src.rag.vectorstore import get_index_stats, get_or_create_vectorstore, get_retriever

OUTPUT_DIR = REPO_ROOT / "output"

_retriever: VectorStoreRetriever | None = None
_index_chunks: list[Document] | None = None


def init_knowledge_base(rebuild: bool = False) -> dict[str, int]:
    """Load or build the vector index and prepare tools that depend on it."""
    global _retriever, _index_chunks

    vectorstore, chunks = get_or_create_vectorstore(rebuild=rebuild)
    _retriever = get_retriever(vectorstore)
    _index_chunks = chunks if chunks else None

    if chunks:
        return get_index_stats(chunks)
    return get_index_stats()


def _format_docs(docs: list[Document]) -> str:
    if not docs:
        return "No matching documentation found."

    parts: list[str] = []
    for index, doc in enumerate(docs, 1):
        filename = doc.metadata.get("filename") or doc.metadata.get("source", "unknown")
        section = doc.metadata.get("section", "")
        header = f"[{index}] {filename}"
        if section:
            header += f" — {section}"
        parts.append(f"{header}\n{doc.page_content.strip()}")

    return "\n\n".join(parts)


@tool
def retail_docs_tool(query: str) -> str:
    """Search Retail Cloud Platform markdown documentation.

    Use for questions about architecture, GitOps, Terraform, GitHub Actions,
    OPA policies, cloud-requests, cloud-infrastructure, and cloud-governance.
    Input should be a natural-language search query.
    """
    if _retriever is None:
        init_knowledge_base()

    docs = _retriever.invoke(query)
    return _format_docs(docs)


@tool
def file_writer_tool(content: str, filename: str = "report.md") -> str:
    """Write text content to a file under the output/ directory.

    Provide the full report content and a filename (for example, report.md).
    Returns the path where the file was saved.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name
    path = OUTPUT_DIR / safe_name
    path.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to {path}"


@tool
def index_stats_tool() -> str:
    """Return statistics about the indexed Retail Cloud Platform documentation.

    Reports the number of source documents and text chunks in the vector index.
    """
    if _index_chunks is not None:
        stats = get_index_stats(_index_chunks)
    else:
        stats = get_index_stats()

    return f"Documents: {stats['documents']}, Chunks: {stats['chunks']}"
