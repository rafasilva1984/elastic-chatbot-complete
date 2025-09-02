import os
from typing import List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from elastic_client import get_es, bm25_search
from prompt import build_prompt
from llm_client import generate_answer

load_dotenv()
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "docs")
DEFAULT_K = 4

app = FastAPI(title="Elasticsearch RAG API", version="1.0.0")

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2)
    k: int = Field(DEFAULT_K, ge=1, le=20)

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    es = get_es()
    hits = bm25_search(es, ELASTIC_INDEX, req.question, size=req.k)
    context_chunks, sources = [], []
    for h in hits:
        src = h.get("_source", {})
        title, body, url = src.get("title",""), src.get("body",""), src.get("url","")
        score = h.get("_score", 0)
        snippet = body[:700]
        context_chunks.append(f"### {title}\n{snippet}\nFonte: {url}")
        sources.append({"title": title, "url": url, "score": score})
    if not context_chunks:
        return AskResponse(answer="Não encontrei contexto relevante no índice.", sources=[])
    context = "\n\n---\n\n".join(context_chunks)
    prompt = build_prompt(req.question, context)
    answer = generate_answer(prompt, fallback_context=context)
    return AskResponse(answer=answer, sources=sources)
