"""
File: tool/tool_rag_pipeline.py
Owner: Member 3 - Priyanshi Saini
Function: Implements the RAG pipeline for job matching.
"""

import os
import shutil
import chromadb
from sentence_transformers import SentenceTransformer
from graph.state import EMBEDDING_MODEL

CHROMA_PATH = os.path.join(".", "data", "processed")
COLLECTION_NAME = "job_listings"

_encoder = None
_chroma_client = None
_collection = None

def _get_encoder() -> SentenceTransformer:
    global _encoder
    if _encoder is None: _encoder = SentenceTransformer(EMBEDDING_MODEL)
    return _encoder

def _get_client() -> chromadb.EphemeralClient:
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        _chroma_client = chromadb.EphemeralClient()
    return _chroma_client

def _get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
        _collection = _chroma_client.get_or_create_collection(name="job_listings")
    return _collection

def reset_database():
    """Recursively deletes the data/processed directory."""
    global _collection, _chroma_client
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"reset_database: Deleted {CHROMA_PATH}")
    _collection = None
    _chroma_client = None

def _build_job_text(job: dict) -> str:
    if not isinstance(job, dict): return ""
    title = job.get("job_title") or job.get("title") or ""
    company = job.get("employer_name") or job.get("company") or ""
    desc = job.get("job_description") or job.get("description") or ""
    return f"Title: {title}\nCompany: {company}\nDescription: {desc}"

def embed_and_store(job_listings: list, clear_existing: bool = True) -> int:
    if not job_listings or not isinstance(job_listings, list): return 0
    
    # Deduplicate by title
    seen_titles = set()
    unique_jobs = []
    for job in job_listings:
        title = (job.get("job_title") or job.get("title") or "").lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_jobs.append(job)

    if clear_existing:
        reset_database()

    collection = _get_collection()
    encoder = _get_encoder()
    docs, metas, ids = [], [], []

    for i, job in enumerate(unique_jobs):
        docs.append(_build_job_text(job))
        metas.append({"title": job.get("job_title") or job.get("title") or ""})
        ids.append(str(i))

    if docs:
        embeddings = encoder.encode(docs).tolist()
        collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
        print(f"embed_and_store: stored {len(ids)} unique job listings.")
    return len(ids)

def retrieve_top_k(query_vector: list, k: int = 5) -> list:
    if not query_vector: return []
    collection = _get_collection()
    if collection.count() == 0: return []
    try:
        results = collection.query(query_embeddings=[query_vector], n_results=min(k, collection.count()))
        documents = results.get("documents", [[]])
        return documents[0] if documents else []
    except Exception as e:
        print(f"retrieve_top_k failed: {e}")
        return []
    
"""
if __name__ == "__main__":
    import json
    
    # 1. Load the file
    path = os.path.join("data", "rawFolder", "sample_jobs.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle if your JSON is {"jobs": [...]} or just [...]
        jobs = data.get("jobs", data) if isinstance(data, dict) else data

    # 2. Run embed_and_store
    count = embed_and_store(jobs, clear_existing=True)
    print(f"Stored {count} jobs.")

    # 3. Confirm count in ChromaDB
    collection = _get_collection()
    print(f"Verification: Collection count is {collection.count()}")

 """