import os, glob, json
from elastic_client import get_es

INDEX = os.getenv("ELASTIC_INDEX", "docs")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "sample_index_settings.json")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

def ensure_index(es):
    if not es.indices.exists(index=INDEX):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            body = json.load(f)
        es.indices.create(index=INDEX, body=body)
        print(f"Index criado: {INDEX}")
    else:
        print(f"Index já existe: {INDEX}")

def load_docs(es):
    files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.md")))
    if not files:
        print("Nenhum .md em docs/")
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        title = os.path.basename(path).replace("-", " ").replace(".md","")
        es.index(index=INDEX, document={"title": title, "body": text, "url": f"file://{path}"})
        print(f"Indexado: {os.path.basename(path)}")
    es.indices.refresh(index=INDEX)

if __name__ == "__main__":
    es = get_es()
    ensure_index(es)
    load_docs(es)
    print("Ingestão concluída.")
