# 🤖 Chatbot RAG com Elasticsearch + FastAPI

Este projeto entrega um **chatbot corporativo** simples, baseado em **Elasticsearch** para recuperação de contexto (BM25) e **FastAPI** como orquestrador.  
Ele foi desenhado para ser **fácil de subir** com Docker Compose e extensível com LLMs como **OpenAI** ou **Ollama**.  

---

## 📐 Arquitetura

```
[Usuário via UI ou API] ---> [/api/ask] FastAPI ---> Elasticsearch (BM25)
                                   | 
                                   +--> (Opcional) LLM (OpenAI/Ollama)
                                   |
                               Resposta final + fontes
```

- **Elasticsearch**: indexa os documentos em Markdown.  
- **FastAPI**: recebe perguntas, busca os docs relevantes, monta prompt e (opcional) envia para LLM.  
- **UI Web**: página simples em `/static/index.html`.  
- **Telemetria**: cada interação é logada em `chat_logs` no Elasticsearch.  

---

## 🚀 Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/sua-org/elastic-chatbot.git
cd elastic-chatbot
```

### 2. Configure o `.env`
```bash
cp retriever-api/.env.example retriever-api/.env
```

Opções de LLM:
- `none` → responde só com os trechos recuperados.
- `openai:gpt-4o-mini` → usa OpenAI (precisa `OPENAI_API_KEY`).
- `ollama:llama3.1` → usa Ollama local.

### 3. Suba os containers
```bash
docker compose up -d --build
```

### 4. Ingestão de documentos
Coloque arquivos `.md` em `retriever-api/docs/` (já existem alguns exemplos).  
Depois, rode:

```bash
docker compose exec retriever-api python -m scripts.ingest
```

---

## 💬 Exemplos de uso

### API
```bash
curl -s http://localhost:8000/api/ask -H "Content-Type: application/json" -d '{
  "question": "Como está estruturado nosso CI/CD?",
  "k": 3
}'
```

### UI
Abra no navegador:  
👉 [http://localhost:8000/](http://localhost:8000/)  

### Swagger
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📊 Observabilidade e Uso

Toda pergunta/resposta é logada no índice `chat_logs`.  
Você pode explorar via API:

```bash
curl -s http://localhost:8000/usage
```

Ou criar um **Dashboard no Kibana**:
- **Chats ao longo do tempo**  
- **Média do tamanho da resposta**  
- **Tópicos mais perguntados**  
- **% de perguntas com contexto**  

---

## 📂 Estrutura do projeto

```
.
├── docker-compose.yml
├── retriever-api/
│   ├── app.py                 # API principal
│   ├── elastic_client.py      # Cliente ES
│   ├── llm_client.py          # OpenAI/Ollama/none
│   ├── prompt.py              # Template de prompt
│   ├── scripts/
│   │   ├── ingest.py          # Ingestão de docs
│   │   └── sample_index_settings.json
│   ├── docs/                  # Documentos a indexar
│   ├── static/                # UI web simples
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
└── extras/
    └── langflow/flow.json     # Flow opcional no Langflow
```

---

## 🛠️ Próximos passos

- [ ] Adicionar suporte a embeddings (kNN).  
- [ ] Implementar busca híbrida (BM25 + vetores).  
- [ ] Re-ranking com Cross-Encoder ou LLM leve.  
- [ ] Upload de PDFs/HTML com parsing automático.  
- [ ] Dashboard Kibana pronto para uso.  

---

## 📜 Licença
MIT — livre para uso e adaptação.  
