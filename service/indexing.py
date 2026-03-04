#!/usr/bin/env python
# coding: utf-8

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
from dotenv import load_dotenv
import uuid
import os
from service import embedding
from service.embedding import get_embedding

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
environment = os.getenv("PINECONE_ENV")

pc = Pinecone(api_key=api_key, environment=environment)

index_name = "medcube-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws")
    )

index = pc.Index(index_name)

def embed_and_store(chunks):
    vectors = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"] if isinstance(chunk, dict) else chunk
        vector_values = get_embedding(text)
        
        # Build metadata - exclude None values, Pinecone rejects them
        metadata = {"text": text}
        if isinstance(chunk, dict):
            if chunk.get("page_number") is not None:
                metadata["page_number"] = chunk["page_number"]
            if chunk.get("file_name") is not None:
                metadata["file_name"] = chunk["file_name"]
        
        vectors.append({
            "id": str(uuid.uuid4()),  # unique IDs to avoid collisions across uploads
            "values": vector_values if isinstance(vector_values, list) else vector_values.tolist(),
            "metadata": metadata
        })
    print(f"Total vectors: {len(vectors)}")
    print(f"First vector id: {vectors[0]['id']}")
    print(f"First vector dim: {len(vectors[0]['values'])}")
    print(f"First vector metadata: {vectors[0]['metadata']}")
    index.upsert(vectors=vectors)



def hybrid_search(query: str, top_k: int = 5, score_threshold: float = 0.75, metadata_filter: dict = None):
    query_embedding = get_embedding(query)  # just call it directly

    search_kwargs = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True
    }
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    results = index.query(**search_kwargs)

    return [
        match for match in results["matches"]
        if match["score"] >= score_threshold
    ]


if __name__ == "__main__":
    test_embedding = get_embedding("test medical document")
    print(f"EMBEDDING TYPE: {type(test_embedding)}, LEN: {len(test_embedding)}, FIRST: {type(test_embedding[0])}")
    
    test_vector = [{
        "id": "test-id-123",
        "values": test_embedding,
        "metadata": {"text": "test", "page_number": 1, "file_name": "test.pdf"}
    }]
    
    index.upsert(vectors=test_vector)
    print("--- Upsert successful! ---")
    