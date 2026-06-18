"""RAG-specific configuration for the Retail Cloud Platform chatbot."""

from pathlib import Path

from src.config import EMBEDDING_MODEL, LMS_API_BASE, LMS_MODEL_ID

# Repository root (noman-ai-poc/)
REPO_ROOT = Path(__file__).resolve().parents[2]

# Knowledge base
DOCS_PATH = Path("/Users/mohammadnoman/Projects/digital/retail-platform/docs")

# Vector store
CHROMA_PERSIST_DIR = REPO_ROOT / "chroma_db"
COLLECTION_NAME = "retail_platform_docs"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Retrieval
RETRIEVER_K = 5

# LLM (reused from src.config)
LMS_BASE_URL = LMS_API_BASE
LMS_MODEL = LMS_MODEL_ID
EMBEDDINGS_MODEL = EMBEDDING_MODEL

# Generation defaults for RAG answers
RAG_TEMPERATURE = 0.2
RAG_MAX_TOKENS = 1024
