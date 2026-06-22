"""Chroma vector store build, load, and retriever helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings

from src.rag.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDINGS_MODEL,
    RETRIEVER_K,
)
from src.rag.loader import load_and_split_documents


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return the local HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)


def vectorstore_exists(persist_dir: Path | None = None) -> bool:
    """Check whether a persisted Chroma index already exists."""
    path = persist_dir or CHROMA_PERSIST_DIR
    return path.exists() and any(path.iterdir())


def build_vectorstore(
    persist_dir: Path | None = None,
    docs_path: Path | None = None,
) -> Chroma:
    """Load docs, chunk them, embed, and persist a new Chroma index."""
    path = persist_dir or CHROMA_PERSIST_DIR
    if path.exists():
        shutil.rmtree(path)

    chunks = load_and_split_documents(docs_path)
    if not chunks:
        raise ValueError("No document chunks were produced from the knowledge base.")

    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(path),
    )
    return vectorstore


def load_vectorstore(persist_dir: Path | None = None) -> Chroma:
    """Load an existing Chroma index from disk."""
    path = persist_dir or CHROMA_PERSIST_DIR
    if not vectorstore_exists(path):
        raise FileNotFoundError(
            f"No vector store found at {path}. Run with --rebuild to create the index."
        )

    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(path),
    )


def get_or_create_vectorstore(rebuild: bool = False) -> tuple[Chroma, list[Document]]:
    """Load an existing index or build a new one. Returns vectorstore and chunks."""
    if rebuild or not vectorstore_exists():
        chunks = load_and_split_documents()
        vectorstore = build_vectorstore()
        return vectorstore, chunks

    vectorstore = load_vectorstore()
    return vectorstore, []


def get_retriever(vectorstore: Chroma, k: int | None = None) -> VectorStoreRetriever:
    """Return a similarity retriever over the vector store."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k or RETRIEVER_K},
    )


def get_index_stats(chunks: list[Document] | None = None) -> dict[str, int]:
    """Return basic indexing statistics."""
    if chunks is None:
        chunks = load_and_split_documents()

    filenames = {c.metadata.get("filename", "unknown") for c in chunks}
    return {
        "documents": len(filenames),
        "chunks": len(chunks),
    }
