# retriever-api/app.py
import os
from typing import List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from elastic_client import get_es, bm25_search
from prompt import build_prompt
from llm_client import generate_answer

load_dotenv()

ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "docs")
LOG_INDEX = os.getenv("LOG_INDEX", "chat_logs")  # índice para telemetria
DEFAULT_K = 4

app = FastAPI(title="Elasticsearch RAG API", version="1.1.0")

# Servir UI estática
app.mount("/static", StaticFiles(directory="static"), name="static")

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2)
    k: int = Field(DEFAULT_K, ge=1, le=20)

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@app.get("/")
def root():
    # redireciona para a UI
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

def log_interaction(es, question: str, answer: str, sources: List[Dict[str, Any]]):
    try:
        es.indices.create(index=LOG_INDEX, ignore=400)
        es.index(index=LOG_INDEX, document={
            "ts": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "question": question,
            "answer_preview": answer[:400],
            "answer_len": len(answer or ""),
            "num_sources": len(sources or []),
            "sources": sources,
        })
    except Exception as e:
        # log silencioso para não quebrar fluxo
        print(f"[log_interaction] falha: {e}")

@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    es = get_es()
    hits = bm25_search(es, ELASTIC_INDEX, req.question, size=req.k)
    context_chunks, sources = [], []
    for h in hits:
        src = h.get("_source", {})
        title, body, url = src.get("title",""), src.get("body",""), src.get("url","")
        score = h.get("_score", 0)
        snippet = (body or "")[:700]
        context_chunks.append(f"### {title}\n{snippet}\nFonte: {url}")
        sources.append({"title": title, "url": url, "score": score})
    if not context_chunks:
        ans = "Não encontrei contexto relevante no índice."
        log_interaction(es, req.question, ans, [])
        return AskResponse(answer=ans, sources=[])

    context = "\n\n---\n\n".join(context_chunks)
    prompt = build_prompt(req.question, context)
    answer = generate_answer(prompt, fallback_context=context)

    # loga a interação
    log_interaction(es, req.question, answer, sources)

    return AskResponse(answer=answer, sources=sources)

@app.get("/usage")
def usage(last: int = 20):
    """Retorna últimos registros de uso básicos do índice de logs."""
    es = get_es()
    try:
        resp = es.search(index=LOG_INDEX, size=last, sort=["ts:desc"], query={"match_all": {}})
        items = [{"ts": h["_source"].get("ts"),
                  "question": h["_source"].get("question"),
                  "answer_len": h["_source"].get("answer_len"),
                  "num_sources": h["_source"].get("num_sources")} for h in resp["hits"]["hits"]]
        total = es.count(index=LOG_INDEX)["count"]
        return {"total": total, "last": items}
    except Exception as e:
        return {"error": str(e), "hint": f"Verifique se o índice {LOG_INDEX} existe e se há documentos."}
