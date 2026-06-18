"""Document loading and chunking for Retail Cloud Platform markdown docs."""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.rag.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_PATH

HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]


def _enrich_metadata(doc: Document) -> Document:
    """Add a human-readable section label from header metadata."""
    headers = [
        doc.metadata.get("Header 1"),
        doc.metadata.get("Header 2"),
        doc.metadata.get("Header 3"),
    ]
    section = " > ".join(h for h in headers if h)
    if section:
        doc.metadata["section"] = section

    source = doc.metadata.get("source", "")
    if source:
        doc.metadata["filename"] = Path(source).name

    return doc


def load_documents(docs_path: Path | None = None) -> list[Document]:
    """Load all markdown files from the docs directory."""
    path = docs_path or DOCS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Documentation directory not found: {path}")

    loader = DirectoryLoader(
        str(path),
        glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
        show_progress=True,
        use_multithreading=True,
    )
    return loader.load()


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents by markdown headers, then by size for oversized chunks."""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )

    header_chunks: list[Document] = []
    for doc in documents:
        splits = header_splitter.split_text(doc.page_content)
        for split in splits:
            split.metadata = {**doc.metadata, **split.metadata}
            header_chunks.append(_enrich_metadata(split))

    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "|", " ", ""],
    )

    final_chunks: list[Document] = []
    for chunk in header_chunks:
        if len(chunk.page_content) <= CHUNK_SIZE:
            final_chunks.append(chunk)
        else:
            sub_chunks = size_splitter.split_documents([chunk])
            for sub in sub_chunks:
                final_chunks.append(_enrich_metadata(sub))

    return final_chunks


def load_and_split_documents(docs_path: Path | None = None) -> list[Document]:
    """Load markdown docs and return chunked documents ready for indexing."""
    documents = load_documents(docs_path)
    return split_documents(documents)
