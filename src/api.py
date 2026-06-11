from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.token_visualizer import TokenVisualizer, EmbeddingVisualizer
from src.config import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

app = FastAPI(title="LLM QnA Bot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm = LLMClient()
prompt_manager = PromptManager()
token_viz = TokenVisualizer()
embed_viz = EmbeddingVisualizer()

class ChatRequest(BaseModel):
    question: str
    role: str = "qa"
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    context: Optional[str] = None

class TokenizeRequest(BaseModel):
    text: str

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

class EmbeddingRequest(BaseModel):
    text: str

@app.get("/roles")
async def get_roles():
    return prompt_manager.get_available_roles()

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        prompt = prompt_manager.create_prompt(
            req.question, 
            role=req.role, 
            context=req.context
        )
        result = llm.generate(
            prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            visualize_tokens=False
        )
        # Add to history
        prompt_manager.add_to_history(req.question, result["response"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tokenize")
async def tokenize(req: TokenizeRequest):
    try:
        return token_viz.visualize_tokens(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embeddings")
async def embeddings(req: EmbeddingRequest):
    try:
        emb = embed_viz.get_embeddings(req.text)
        return {
            "text": req.text,
            "dimension": emb.shape[0],
            "stats": {
                "mean": float(emb.mean()),
                "std": float(emb.std()),
                "min": float(emb.min()),
                "max": float(emb.max()),
            },
            "embedding": emb.tolist()[:100]  # Return first 100 for visualization
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similarity")
async def similarity(req: SimilarityRequest):
    try:
        sim = embed_viz.calculate_similarity(req.text1, req.text2)
        return {"similarity": sim}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    return [{"question": q, "answer": a} for q, a in prompt_manager.conversation_history]

@app.delete("/history")
async def clear_history():
    prompt_manager.clear_history()
    return {"message": "History cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
