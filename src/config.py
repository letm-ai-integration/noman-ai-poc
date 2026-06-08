"""Configuration settings for the LLM QnA Bot"""

# Model Configuration
MODEL_NAME = "distilgpt2"  # Lightweight model for fast inference
# Alternative: "gpt2", "distilbert-base-uncased" (for embeddings)

# Generation Parameters (can be overridden via CLI)
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Visualization
ENABLE_TOKEN_VISUALIZATION = True
ENABLE_EMBEDDING_VISUALIZATION = True

# Prompt Roles
SYSTEM_ROLES = {
    "assistant": "You are a helpful AI assistant.",
    "qa": "You are an expert QnA assistant. Answer questions concisely and accurately.",
    "tutor": "You are an educational tutor. Explain concepts clearly with examples.",
    "creative": "You are a creative writer. Generate imaginative and engaging content.",
}

# API Configuration
DEVICE = "cpu"  # Use "cuda" if GPU available
