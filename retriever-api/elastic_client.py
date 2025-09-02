import os
from elasticsearch import Elasticsearch

def get_es() -> Elasticsearch:
    url = os.getenv("ELASTIC_URL", "http://localhost:9200")
    return Elasticsearch(url, request_timeout=30)

def bm25_search(es: Elasticsearch, index: str, query: str, size: int = 4):
    resp = es.search(index=index, query={"multi_match": {"query": query, "fields": ["title^2","body"]}}, size=size)
    return resp["hits"]["hits"]
