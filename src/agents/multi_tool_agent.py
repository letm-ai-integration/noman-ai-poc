#!/usr/bin/env python3
"""Multi-tool LangGraph ReAct agent with docs, web search, Python, and file I/O."""

from __future__ import annotations

import argparse
import sys

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_experimental.tools import PythonREPLTool
from langgraph.prebuilt import create_react_agent

from src.agents.tools import (
    file_writer_tool,
    index_stats_tool,
    init_knowledge_base,
    retail_docs_tool,
)
from src.rag.chain import create_llm


def build_agent():
    """Build a LangGraph ReAct agent with five tools."""
    llm = create_llm()
    tools = [
        retail_docs_tool,
        DuckDuckGoSearchRun(),
        PythonREPLTool(),
        file_writer_tool,
        index_stats_tool,
    ]
    return create_react_agent(llm, tools)


def _extract_final_answer(messages: list) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            if not message.tool_calls:
                return message.content
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return "No response generated."


def run_agent(agent, question: str, verbose: bool = True) -> str:
    """Run the agent and optionally print tool-call steps."""
    inputs = {"messages": [HumanMessage(content=question)]}
    final_answer = ""

    if verbose:
        print(f"Question: {question}\n")

    for chunk in agent.stream(inputs, stream_mode="updates"):
        for _step, data in chunk.items():
            messages = data.get("messages", [])
            for message in messages:
                if isinstance(message, AIMessage):
                    if message.tool_calls and verbose:
                        for tool_call in message.tool_calls:
                            print(f"  -> Tool: {tool_call['name']}({tool_call['args']})")
                    elif message.content:
                        final_answer = message.content
                elif isinstance(message, ToolMessage) and verbose:
                    preview = message.content
                    if len(preview) > 200:
                        preview = preview[:200] + "..."
                    print(f"  <- Observation: {preview}")

    if not final_answer:
        result = agent.invoke(inputs)
        final_answer = _extract_final_answer(result.get("messages", []))

    return final_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multi-tool LangGraph agent (docs, web, Python, file writer, stats)",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Task for the agent (omit for interactive mode)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild of the Chroma vector index from markdown docs",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose tool-call logging",
    )
    return parser.parse_args()


def run_once(agent, question: str, verbose: bool) -> int:
    try:
        answer = run_agent(agent, question, verbose=verbose)
        print(f"\nFinal Answer:\n{answer}\n")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Ensure LM Studio is running with a model loaded at "
            "http://localhost:1234/v1",
            file=sys.stderr,
        )
        return 1
    return 0


def run_interactive(agent, verbose: bool) -> int:
    print("Interactive mode. Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return 0

        try:
            answer = run_agent(agent, question, verbose=verbose)
            print(f"\nFinal Answer:\n{answer}\n")
        except Exception as exc:
            print(f"Error: {exc}\n", file=sys.stderr)
            print(
                "Ensure LM Studio is running at http://localhost:1234/v1\n",
                file=sys.stderr,
            )


def main() -> int:
    args = parse_args()

    print("Initializing knowledge base...")
    stats = init_knowledge_base(rebuild=args.rebuild)
    print(f"Index ready ({stats['documents']} docs, {stats['chunks']} chunks)\n")

    print("Building multi-tool agent...")
    agent = build_agent()
    verbose = not args.quiet

    if args.question:
        return run_once(agent, args.question, verbose=verbose)
    return run_interactive(agent, verbose=verbose)


if __name__ == "__main__":
    sys.exit(main())
