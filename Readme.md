# LLM QnA Bot with Token Visualization

A pure Python implementation of an interactive QnA bot with LLM (Large Language Model) using open-source libraries. Includes token visualization, embedding analysis, and temperature experimentation.

## Features

✨ **Core Features:**
- Interactive CLI-based QnA bot
- Role-based prompting (QA, Tutor, Creative, Assistant)
- Token visualization and analysis
- Embedding visualization and similarity calculation
- Temperature and max_tokens experimentation
- Conversation history management

📚 **RAG Chatbot (Retail Cloud Platform Docs):**
- Conversational retrieval-augmented generation over local markdown docs
- LangChain + Chroma vector store with persistent local index
- History-aware follow-up questions via LM Studio

🚀 **No Heavy Frameworks (core QnA bot):**
- Pure Python implementation
- No Langchain/Langgraph dependencies in the base CLI/API
- Direct HuggingFace transformers library
- Lightweight models (distilgpt2, sentence-transformers)

## Project Structure

```
noman-ai-poc/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI entry point
│   ├── config.py                # Configuration settings
│   ├── llm_client.py            # LLM generation logic
│   ├── prompt_manager.py        # Role-based prompts
│   ├── token_visualizer.py      # Token & embedding visualization
│   └── rag/                     # Retail Cloud Platform RAG chatbot
│       ├── config.py            # RAG paths and chunk settings
│       ├── loader.py            # Markdown doc loading and splitting
│       ├── vectorstore.py       # Chroma index build/load
│       ├── chain.py             # History-aware retrieval chain
│       └── cli.py               # RAG interactive CLI
├── requirements.txt             # Python dependencies (core bot)
├── requirements_rag.txt         # Additional RAG dependencies
├── setup.sh                     # Setup script
└── README.md                    # This file
```

## Installation

### 1. Clone and Navigate to Project

```bash
cd /Users/mohammadnoman/Projects/digital/LETM-AI/noman-ai-poc
```

### 2. Create Virtual Environment

```bash
# Using Python 3.9+
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** First run will download ~1GB of models (distilgpt2 + embeddings). Subsequent runs will be faster.

## Usage

### Interactive Mode (Default)

```bash
python -m src.main --mode interactive
```

**Interactive Commands:**
```
ask <question>              - Ask a question
role <role_name>            - Change role (qa, tutor, creative, assistant)
temp <value>                - Set temperature (0.1-2.0)
tokens <value>              - Set max tokens
visualize <text>            - Visualize tokens
embedding <text>            - Get embedding information
similarity <text1|text2>     - Compare text similarity
history                     - Show conversation history
clear                       - Clear history
roles                       - List available roles
help                        - Show help
exit/quit                   - Exit
```

**Example Interactive Session:**
```bash
> ask What is machine learning?
> role tutor
> temp 1.2
> ask Explain neural networks
> visualize "Hello world"
> similarity "AI is cool|Machine learning is interesting"
> exit
```

### Single Question Mode

```bash
# Basic question
python -m src.main --mode single --question "What is Python?"

# With custom role and parameters
python -m src.main --question "Write a poem" --role creative --temperature 1.5 --max-tokens 80

# Compare different temperatures
python -m src.main --question "Tell a story" --compare-temps

# Compare different token limits
python -m src.main --question "Explain AI" --compare-tokens
```

### Token Analysis

```bash
# Visualize tokens for text
python -m src.main --analyze-tokens "Hello, how are you?"
```

### Embedding Visualization

```bash
# Get embedding info for single text
python -m src.main --visualize-embeddings "What is AI?"

# Compare multiple texts with similarity matrix
python -m src.main --visualize-embeddings "AI is smart" "ML is powerful" "NLP is complex"
```

### Similarity Calculation

```bash
python -m src.main --similarity "The cat sat on the mat" "A cat was sitting on a mat"
```

## Retail Cloud Platform RAG Chatbot

A separate LangChain-based module that answers questions about the Retail Cloud Platform using markdown documentation from `retail-platform/docs`. It uses LM Studio for generation, HuggingFace embeddings locally, and a persisted Chroma index.

### Prerequisites

1. **LM Studio** running with a model loaded and the local server enabled at `http://localhost:1234/v1`
2. **Documentation** available at `/Users/mohammadnoman/Projects/digital/retail-platform/docs`

### Install RAG Dependencies

From the repo root with your virtual environment activated:

```bash
pip install -r requirements.txt -r requirements_rag.txt
```

The first run downloads the embedding model (`sentence-transformers/all-MiniLM-L6-v2`) if it is not already cached.

### Run the RAG Chatbot

```bash
python -m src.rag.cli
```

On the first run, the CLI builds a Chroma index from the markdown docs (about 30 seconds) and saves it to `./chroma_db/`. Later runs load the saved index instantly.

To force a rebuild after docs change:

```bash
python -m src.rag.cli --rebuild
```

### RAG CLI Commands

Once started, type questions at the `You:` prompt:

```
You: What are the three repositories in the Retail Cloud Platform?
You: How does cloud-requests dispatch to cloud-infrastructure?
You: What known gaps exist in cross-repo integration?
```

| Command | Action |
|---------|--------|
| `exit` / `quit` | Exit the chatbot |
| `clear` | Reset conversation history |
| `sources` | Toggle source citations on/off |
| `help` | Show help |

### RAG Configuration

Edit `src/rag/config.py` to customize:

- `DOCS_PATH` — path to the markdown documentation directory
- `CHROMA_PERSIST_DIR` — local vector store location (default: `./chroma_db/`)
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — document chunking settings
- `RETRIEVER_K` — number of chunks retrieved per question

LM Studio settings are reused from `src/config.py` (`LMS_API_BASE`, `LMS_MODEL_ID`).

### RAG Troubleshooting

**Documentation directory not found**

Verify `DOCS_PATH` in `src/rag/config.py` points to your docs folder.

**Connection errors to LM Studio**

Open LM Studio, load a chat model, and start the local server on port `1234`.

**Missing packages**

```bash
pip install -r requirements_rag.txt
```

### Quick Start (RAG)

```bash
cd /Users/mohammadnoman/Projects/digital/LETM-AI/noman-ai-poc
source .venv/bin/activate
pip install -r requirements.txt -r requirements_rag.txt
python -m src.rag.cli
```

## Configuration

Edit `src/config.py` to customize:

```python
# Model Selection
MODEL_NAME = "distilgpt2"  # Lightweight model
# Alternatives: "gpt2", "distilbert-base-uncased"

# Generation Parameters
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMPERATURE = 0.7

# Roles
SYSTEM_ROLES = {
    "qa": "You are an expert QnA assistant...",
    "tutor": "You are an educational tutor...",
    # ... more roles
}

# Device
DEVICE = "cpu"  # Use "cuda" if GPU available
```

## Understanding Parameters

### Temperature (0.1 - 2.0)

Controls randomness in responses:
- **Low (0.1-0.3):** Deterministic, focused, conservative
  ```
  Q: What is 2+2?
  A: The answer is 4.
  ```

- **Medium (0.7-0.9):** Balanced, natural (recommended)
  ```
  Q: What is 2+2?
  A: Two plus two equals four.
  ```

- **High (1.2-2.0):** Creative, diverse, unpredictable
  ```
  Q: What is 2+2?
  A: If you add two and two together, you get four, which is also...
  ```

**Experiment:** Use `--compare-temps` to see variations!

### Max Tokens

Controls response length:
- **30 tokens:** Short, concise answers
- **60 tokens:** Medium detailed responses
- **100 tokens:** Longer, more detailed answers
- **512 tokens:** Full detailed explanations

**Experiment:** Use `--compare-tokens` to see length variations!

## Token Visualization

Tokens are the building blocks that LLMs process. Each word/subword = 1 token.

```
Text: "Hello world"
Tokens: ["Hello", "Ġworld"]
Token IDs: [15496, 995]
Total Tokens: 2
```

**What You'll See:**
- Individual tokens (with special character representations)
- Token IDs (internal model representation)
- Token efficiency (tokens per character)

## Embedding Visualization

Embeddings are numerical vectors representing semantic meaning.

**What You'll See:**
- Embedding dimension (length of vector)
- Statistical info (mean, std, min, max)
- Similarity scores between texts (0-1 scale)

**Example:**
- "AI is cool" vs "Machine learning is great" → ~0.75 similarity
- "The cat sat" vs "A dog ran" → ~0.30 similarity

## Available Roles

### QA Role
Expert question-answering assistant - concise, accurate answers

### Tutor Role
Educational focus - explains concepts with examples

### Creative Role
Creative writing - imaginative and engaging responses

### Assistant Role
General purpose - helpful with various tasks

## Examples

### Example 1: Basic QnA

```bash
$ python -m src.main --question "What is Python?" --role qa
```

**Output:**
```
Token Visualization for prompt...
[Tokens shown with IDs]

Generation Result:
Prompt: You are an expert QnA assistant...
Response: Python is a high-level programming language...

Token Usage:
  Prompt Tokens: 45
  Response Tokens: 28
  Total Tokens: 73
```

### Example 2: Temperature Comparison

```bash
$ python -m src.main --question "Tell a short story" --compare-temps
```

**Output:**
```
Temperature Comparison - 3 variations
[Temperature: 0.3] Response: Once upon a time, there was a boy...
[Temperature: 0.7] Response: In a land far away, a young hero...
[Temperature: 1.2] Response: Perhaps you would like to hear about...
```

### Example 3: Embedding Similarity

```bash
$ python -m src.main --visualize-embeddings \
    "Machine learning is powerful" \
    "Deep learning uses neural networks" \
    "Artificial intelligence is the future"
```

**Output:**
```
Similarity Matrix:
Text                          T0        T1        T2
Machine learning...           1.0000    0.7234    0.6891
Deep learning...              0.7234    1.0000    0.5432
Artificial intelligence...    0.6891    0.5432    1.0000
```

## Troubleshooting

### Issue: Out of Memory

**Solution:** Use a smaller model or reduce max_tokens
```python
# In config.py
MODEL_NAME = "distilgpt2"  # Already small
DEFAULT_MAX_TOKENS = 50    # Reduce this
```

### Issue: Slow First Run

**Solution:** First run downloads models (~1GB). Subsequent runs are cached locally.

### Issue: CUDA/GPU Not Found

**Solution:** Falls back to CPU automatically. Edit config.py to force:
```python
DEVICE = "cpu"  # or "cuda"
```

## Model Information

- **LLM Model:** distilgpt2 (82MB)
  - Lightweight version of GPT-2
  - ~82M parameters
  - Fast inference on CPU

- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (~27MB)
  - Semantic similarity calculation
  - 384-dimensional embeddings

Both models are open-source and free to use.

## Advanced Usage

### Custom Roles

Edit `src/config.py` to add custom roles:

```python
SYSTEM_ROLES = {
    "detective": "You are a detective solving a mystery...",
    "chef": "You are a professional chef...",
}
```

### Batch Processing

```python
from src.llm_client import LLMClient

llm = LLMClient()
questions = ["What is AI?", "Explain ML", "What is DL?"]
results = llm.batch_generate(
    [f"Q: {q}\nA:" for q in questions],
    max_tokens=100,
    temperature=0.7
)
```

### Programmatic Usage

```python
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.token_visualizer import EmbeddingVisualizer

# Initialize
llm = LLMClient()
pm = PromptManager()
ev = EmbeddingVisualizer()

# Generate
prompt = pm.create_prompt("What is AI?", role="qa")
result = llm.generate(prompt, max_tokens=100, temperature=0.8)

# Analyze
similarity = ev.calculate_similarity("AI", "Artificial Intelligence")
print(f"Similarity: {similarity}")
```

## Performance Tips

1. **Reduce max_tokens** for faster responses (default: 100)
2. **Use lower temperature** (0.3-0.5) for faster, more deterministic output
3. **Batch process** similar questions together
4. **Use CPU** for lightweight models (faster than GPU overhead for small models)

## Dependencies

- **transformers:** LLM model loading and inference
- **torch:** Deep learning framework
- **numpy:** Numerical computations
- **scipy:** Similarity calculations
- **matplotlib/plotly:** Visualization (optional)
- **python-dotenv:** Environment configuration

## License

Open source - feel free to use and modify!

## Notes

- All models are downloaded on first use (requires internet)
- Models are cached locally in `~/.cache/huggingface/`
- No API keys or authentication required
- Fully offline after first model download
- CPU-friendly implementation

## Future Enhancements

- [ ] Add more LLM models (Llama, Mistral, etc.)
- [ ] Fine-tuning on custom datasets
- [ ] Advanced embedding visualizations (t-SNE, UMAP)
- [x] Multi-turn conversation with context (RAG chatbot)
- [ ] Performance benchmarking
- [ ] Export conversation history

## Support

For issues or questions, check the examples above or modify configurations in `src/config.py`.

Happy experimenting with LLMs! 🚀
