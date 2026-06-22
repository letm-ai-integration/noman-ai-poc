#!/usr/bin/env python3
"""Single-tool ReAct agent over Retail Cloud Platform documentation."""

from __future__ import annotations

import argparse
import sys

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.agents.tools import init_knowledge_base, retail_docs_tool
from src.rag.config import LMS_BASE_URL, LMS_MODEL, RAG_MAX_TOKENS, RAG_TEMPERATURE

REACT_PROMPT = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)


def create_llm() -> ChatOpenAI:
    """Create a ChatOpenAI client pointed at the local LM Studio server."""
    return ChatOpenAI(
        base_url=LMS_BASE_URL,
        api_key="lm-studio",
        model=LMS_MODEL,
        temperature=RAG_TEMPERATURE,
        max_tokens=RAG_MAX_TOKENS,
    )


def build_executor(verbose: bool = True) -> AgentExecutor:
    """Build a ReAct agent with a single documentation search tool."""
    llm = create_llm()
    tools = [retail_docs_tool]
    agent = create_react_agent(llm, tools, REACT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=5,
    )


def run_question(executor: AgentExecutor, question: str) -> str:
    """Run the agent on a single question and return the final answer."""
    result = executor.invoke({"input": question})
    return result.get("output", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Single-tool ReAct agent (Retail Cloud Platform docs)",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask the agent (omit for interactive mode)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild of the Chroma vector index from markdown docs",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose agent logging",
    )
    return parser.parse_args()


def run_once(executor: AgentExecutor, question: str) -> int:
    print(f"Question: {question}\n")
    try:
        answer = run_question(executor, question)
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


def run_interactive(executor: AgentExecutor) -> int:
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
            answer = run_question(executor, question)
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

    executor = build_executor(verbose=not args.quiet)

    if args.question:
        return run_once(executor, args.question)
    return run_interactive(executor)


if __name__ == "__main__":
    sys.exit(main())
