"""
File: tool/tool_rag_pipeline.py
Owner: Member 3 (Job Matching + RAG Pipeline)
Function: Implements the actual RAG mechanics — embeds job descriptions with
          all-MiniLM-L6-v2 (EMBEDDING_MODEL, shared with Member 2 so query
          and document vectors live in the same space), persists them in a
          ChromaDB collection under data/processed/, and retrieves the top-k
          semantically similar jobs given a query embedding. This is
          Steps 2-5 of the RAG pipeline described in the team docs.
Location: tool/ folder — called by agent/agent_jobs.py.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from graph.state import EMBEDDING_MODEL

PERSIST_PATH = "data/processed"
COLLECTION_NAME = "jobs"

# Loaded once at import time — SentenceTransformer + ChromaDB client are both
# expensive to spin up, so we don't want a fresh instance per function call.
_embedder = SentenceTransformer(EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=PERSIST_PATH)


def _job_to_text(job: dict) -> str:
    """
    Builds the text blob that gets embedded for a single job listing.
    Combines title + employer + description so semantic search can match on
    role, company context, and required skills all at once.
    """
    title = job.get("job_title", "Unknown role")
    employer = job.get("employer_name", "Unknown company")
    description = job.get("job_description", "")
    return f"{title} at {employer}. {description}"


def embed_and_store(job_listings: list, collection_name: str = COLLECTION_NAME):
    """
    Embeds each raw job listing and stores it in the ChromaDB collection.

    Args:
        job_listings: raw job dicts from tool_jsearch.search_jobs()
        collection_name: ChromaDB collection to write to (defaults to "jobs")

    Returns:
        The ChromaDB Collection object (useful for chaining / testing).

    Note: uses upsert-by-index IDs, so re-running this on the same
    job_listings list simply overwrites the previous vectors instead of
    duplicating them.
    """
    collection = _client.get_or_create_collection(collection_name)

    if not job_listings:
        print("[tool_rag_pipeline] No job listings to embed — skipping store.")
        return collection

    ids, embeddings, metadatas, documents = [], [], [], []
    for i, job in enumerate(job_listings):
        text = _job_to_text(job)
        embeddings.append(_embedder.encode(text).tolist())
        ids.append(str(i))
        documents.append(text)
        metadatas.append({
            "title": job.get("job_title", "Unknown role"),
            "company": job.get("employer_name", "Unknown company"),
            "apply_link": job.get("job_apply_link", ""),
        })

    # upsert (not add) so re-running the pipeline for the same role doesn't
    # error out on duplicate IDs
    collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
    return collection


def retrieve_top_k(query, k: int = 5, collection_name: str = COLLECTION_NAME) -> list:
    """
    Runs a semantic similarity search over the stored job vectors.

    Args:
        query: EITHER a raw query string (e.g. "Python SQL machine learning")
               which gets encoded with the same all-MiniLM-L6-v2 model used
               for storage, OR a precomputed embedding vector (list[float] of
               length 384). In production, agent_jobs.py passes
               state["resume_embedding"] directly as the precomputed-vector
               form, since Member 2 already encoded it with the same model —
               re-encoding it here would be redundant. The string form exists
               for standalone testing and any caller that only has text.
        k: number of top matches to return

    Returns:
        list[dict]: each dict has "document" (the embedded text), "metadata"
        (title/company/apply_link), and "distance" (lower = more similar).
        Returns [] if the collection is empty.
    """
    # Encode if we were handed raw text; pass through if already a vector.
    query_embedding = embed_text(query) if isinstance(query, str) else query

    collection = _client.get_or_create_collection(collection_name)

    if collection.count() == 0:
        print("[tool_rag_pipeline] Collection is empty — nothing to retrieve. "
              "Did you call embed_and_store() first?")
        return []

    k = min(k, collection.count())
    results = collection.query(query_embeddings=[query_embedding], n_results=k)

    retrieved = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        retrieved.append({"document": doc, "metadata": meta, "distance": dist})
    return retrieved


def embed_text(text: str) -> list:
    """Convenience helper — embeds a raw string using the shared model.
    Mainly useful for manual testing or if a caller only has text, not a
    precomputed embedding, on hand."""
    return _embedder.encode(text).tolist()


if __name__ == "__main__":
    # Manual test: run `python tool/tool_rag_pipeline.py` from the project root.

    # ---------- Day 2: sanity-check the embedding model ----------
    # Encode one sentence and confirm the vector shape is (384,) — this is
    # the fixed output size of all-MiniLM-L6-v2, and it must match the
    # dimensionality of Member 2's resume_embedding for retrieval to work.
    import numpy as np
    sample_vector = _embedder.encode("Sample sentence for shape check")
    print("Day 2 check — embedding shape:", np.array(sample_vector).shape)  # expect (384,)

    # ---------- Day 3: embed_and_store() + ChromaDB count check ----------
    import json
    with open("data/rawFolder/sample_jobs.json", "r", encoding="utf-8") as f:
        sample_jobs = json.load(f)

    print(f"\nLoaded {len(sample_jobs)} jobs from data/rawFolder/sample_jobs.json")
    collection = embed_and_store(sample_jobs)
    print("ChromaDB collection count after embed_and_store():", collection.count())

    # ---------- Day 3: retrieval test ----------
    # retrieve_top_k now accepts the raw query string directly and encodes
    # it internally with the same model used for storage.
    test_query = "Python SQL machine learning"
    print(f"\nQuerying with: '{test_query}'")
    top_matches = retrieve_top_k(test_query, k=3)

    print("\nTop matches (viva evidence — lower distance = more similar):")
    for match in top_matches:
        print(f"- {match['metadata']['title']} @ {match['metadata']['company']} "
              f"(distance={match['distance']:.4f})")