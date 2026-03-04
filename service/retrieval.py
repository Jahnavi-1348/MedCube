#!/usr/bin/env python
# coding: utf-8

import fitz
from service.indexing import embed_and_store
from service.summarize import summarize_text
from service.embedding import get_embedding

def chunk_pdf(file_path: str, chunk_size: int = 500):
    doc = fitz.open(file_path)
    chunks = []
    
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if not text.strip():
            continue
        
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            chunks.append({
                "text": chunk_text,
                "page_number": page_num + 1,
                "file_name": file_path
            })
    
    embed_and_store(chunks)
    print(f"Indexed {len(chunks)} chunks from {file_path}")


def smart_retrieve(query, retriever, metadata_filter=None, score_threshold=0.75):
    results = retriever.get_relevant_documents(query)

    filtered_results = [ 
        doc for doc in results 
        if (not metadata_filter or all(doc.metadata.get(k) == v for k, v in metadata_filter.items())) 
        and doc.metadata.get("score", 1) >= score_threshold
    ]

    combined_text = " ".join([doc.page_content for doc in filtered_results])

    if not combined_text.strip():
        return "No relevant content found."

    summary = summarize_text(combined_text)
    return {
        "summary": summary,
        "raw_chunks": [doc.page_content for doc in filtered_results],
        "metadata": [doc.metadata for doc in filtered_results]
    }



def retrieve_by_query_only(query: str, top_k: int = 5, score_threshold: float = 0.75):
    query_vector = get_embedding(query)

    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    return [match for match in response["matches"] if match["score"] >= score_threshold]




def retrieve_by_query_and_metadata(query: str, metadata_filter: dict, top_k: int = 5, score_threshold: float = 0.75):
    query_vector = get_embedding(query)

    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=metadata_filter
    )

    return [match for match in response["matches"] if match["score"] >= score_threshold]


def smart_retrieve(query: str, metadata_filter: dict = None, top_k: int = 5, score_threshold: float = 0.75):
    if metadata_filter:
        return retrieve_by_query_and_metadata(query, metadata_filter, top_k, score_threshold)
    return retrieve_by_query_only(query, top_k, score_threshold)


if __name__ == "__main__":
    print("--- script finished successfully! ---")