import os, json, httpx
LLM_MODEL = os.getenv("LLM_MODEL", "none")

def _openai_chat(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise RuntimeError("OPENAI_API_KEY não configurada")
    _, model = LLM_MODEL.split(":", 1)
    r = httpx.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"},
        json={"model": model, "messages":[
            {"role":"system","content":"Responda em português do Brasil."},
            {"role":"user","content": prompt}
        ], "temperature": 0.2}, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def _ollama_chat(prompt: str) -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    _, model = LLM_MODEL.split(":", 1)
    r = httpx.post(f"{host}/api/chat",
        json={"model": model, "messages":[
            {"role":"system","content":"Responda em português do Brasil."},
            {"role":"user","content": prompt}
        ], "options":{"temperature":0.2}}, timeout=120)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        if "message" in data and isinstance(data["message"], dict) and "content" in data["message"]:
            return data["message"]["content"].strip()
        if "content" in data and isinstance(data["content"], str):
            return data["content"].strip()
    return json.dumps(data)

def generate_answer(prompt: str, fallback_context: str = "") -> str:
    try:
        if LLM_MODEL.startswith("openai:"):
            return _openai_chat(prompt)
        if LLM_MODEL.startswith("ollama:"):
            return _ollama_chat(prompt)
        return f"(Modo sem LLM) Contexto relevante:\n\n{fallback_context[:1500]}"
    except Exception as e:
        return f"[Aviso] Falha ao gerar com LLM: {e}\n\nResumo do contexto:\n{fallback_context[:1200]}"
