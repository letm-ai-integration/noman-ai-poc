"""Conversational retrieval chain with chat history for RAG Q&A."""

from __future__ import annotations

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI

from src.rag.config import LMS_BASE_URL, LMS_MODEL, RAG_MAX_TOKENS, RAG_TEMPERATURE

CONTEXTUALIZE_Q_SYSTEM_PROMPT = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood without the chat history. "
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)

QA_SYSTEM_PROMPT = """You are a DevOps Platform Engineering Assistant for the Retail Cloud Platform.

Your role is to help engineers understand the platform's architecture, GitOps workflows, Terraform stacks,
GitHub Actions automation, Python request processors, OPA/Conftest governance policies, and cross-repository integrations.

Answer questions strictly based on the retrieved documentation context below.
If the answer is not contained in the context, respond with:
"I don't have enough information in the documentation to answer that question."
Do not speculate or use knowledge outside the provided context.

Retrieved context:
{context}"""

_session_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return (or create) in-memory chat history for a session."""
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


def clear_session_history(session_id: str) -> None:
    """Clear chat history for a session."""
    if session_id in _session_store:
        _session_store[session_id].clear()


def create_llm() -> ChatOpenAI:
    """Create a ChatOpenAI client pointed at the local LM Studio server."""
    return ChatOpenAI(
        base_url=LMS_BASE_URL,
        api_key="lm-studio",
        model=LMS_MODEL,
        temperature=RAG_TEMPERATURE,
        max_tokens=RAG_MAX_TOKENS,
        streaming=True,
    )


def create_rag_chain(
    retriever: VectorStoreRetriever,
    session_id: str = "default",
) -> RunnableWithMessageHistory:
    """Build a history-aware conversational retrieval chain."""
    llm = create_llm()

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt,
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", QA_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


def format_sources(context_docs: list) -> list[str]:
    """Format retrieved source documents for CLI display."""
    seen: set[str] = set()
    formatted: list[str] = []

    for doc in context_docs[:3]:
        filename = doc.metadata.get("filename") or doc.metadata.get("source", "unknown")
        section = doc.metadata.get("section", "")
        label = f"{filename}"
        if section:
            label = f"{filename} — {section}"
        if label not in seen:
            seen.add(label)
            formatted.append(label)

    return formatted
