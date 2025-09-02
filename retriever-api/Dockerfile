# retriever-api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copia os requisitos primeiro (para cache de build)
COPY requirements.txt ./

# Instala dependências, pulando verificação de SSL no PyPI
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
      --trusted-host pypi.org \
      --trusted-host files.pythonhosted.org \
      -r requirements.txt

# Copia todo o código da aplicação
COPY . .

EXPOSE 8000

# Comando padrão do container
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
