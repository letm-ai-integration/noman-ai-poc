#!/usr/bin/env python3
"""Interactive CLI for the Retail Cloud Platform RAG chatbot."""

from __future__ import annotations

import argparse
import sys

from langchain_core.messages import AIMessageChunk

from src.rag.chain import clear_session_history, create_rag_chain, format_sources
from src.rag.config import DOCS_PATH
from src.rag.vectorstore import get_index_stats, get_or_create_vectorstore, get_retriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retail Cloud Platform RAG chatbot (LangChain + LM Studio)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild of the Chroma vector index from markdown docs",
    )
    parser.add_argument(
        "--session-id",
        default="default",
        help="Session ID for conversation memory (default: default)",
    )
    return parser.parse_args()


def print_banner(stats: dict[str, int], rebuilt: bool) -> None:
    action = "Built" if rebuilt else "Loaded"
    print("=" * 72)
    print("  Retail Cloud Platform — DevOps Platform Engineering Assistant")
    print("=" * 72)
    print(f"  Knowledge base : {DOCS_PATH}")
    print(f"  Index status   : {action} ({stats['documents']} docs, {stats['chunks']} chunks)")
    print()
    print("  Commands: exit | quit | clear | sources | help")
    print("=" * 72)
    print()


def print_help() -> None:
    print(
        "\n".join(
            [
                "",
                "Commands:",
                "  exit, quit   — exit the chatbot",
                "  clear        — clear conversation history",
                "  sources      — toggle showing source citations",
                "  help         — show this help message",
                "",
                "Ask questions about cloud-requests, cloud-infrastructure,",
                "cloud-governance, Terraform stacks, workflows, and OPA policies.",
                "",
            ]
        )
    )


def stream_response(rag_chain, question: str, session_id: str) -> dict:
    """Stream the LLM response token-by-token and return the full result."""
    print("\nAssistant: ", end="", flush=True)
    answer_parts: list[str] = []
    context_docs = []

    config = {"configurable": {"session_id": session_id}}

    for chunk in rag_chain.stream({"input": question}, config=config):
        if "answer" in chunk:
            token = chunk["answer"]
            if isinstance(token, AIMessageChunk):
                text = token.content
            else:
                text = str(token)
            if text:
                print(text, end="", flush=True)
                answer_parts.append(text)
        if "context" in chunk and chunk["context"]:
            context_docs = chunk["context"]

    print("\n")
    return {"answer": "".join(answer_parts), "context": context_docs}


def run_interactive(args: argparse.Namespace) -> int:
    show_sources = True

    print("Initializing vector store...")
    vectorstore, chunks = get_or_create_vectorstore(rebuild=args.rebuild)
    retriever = get_retriever(vectorstore)

    if chunks:
        stats = get_index_stats(chunks)
        rebuilt = True
    else:
        stats = get_index_stats()
        rebuilt = False

    rag_chain = create_rag_chain(retriever, session_id=args.session_id)
    print_banner(stats, rebuilt)

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not question:
            continue

        lowered = question.lower()
        if lowered in {"exit", "quit"}:
            print("Goodbye.")
            return 0
        if lowered == "clear":
            clear_session_history(args.session_id)
            print("Conversation history cleared.\n")
            continue
        if lowered == "sources":
            show_sources = not show_sources
            state = "on" if show_sources else "off"
            print(f"Source citations: {state}\n")
            continue
        if lowered == "help":
            print_help()
            continue

        try:
            result = stream_response(rag_chain, question, args.session_id)
        except Exception as exc:
            print(f"\nError: {exc}\n", file=sys.stderr)
            print(
                "Ensure LM Studio is running with a model loaded at "
                "http://localhost:1234/v1\n",
                file=sys.stderr,
            )
            continue

        if show_sources and result.get("context"):
            sources = format_sources(result["context"])
            if sources:
                print("Sources:")
                for source in sources:
                    print(f"  - {source}")
                print()


def main() -> int:
    args = parse_args()
    return run_interactive(args)


if __name__ == "__main__":
    sys.exit(main())
