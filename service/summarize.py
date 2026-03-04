#!/usr/bin/env python
# coding: utf-8
from dotenv import load_dotenv
load_dotenv()
import requests
import os
from typing import List, Dict, Optional

HF_API_KEY = os.getenv("HF_API_KEY")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
HF_SUMMARIZE_URL = "https://router.huggingface.co/hf-inference/models/sshleifer/distilbart-cnn-12-6"

def call_summarizer(text: str, max_length: int = 150, min_length: int = 20):
    response = requests.post(
        HF_SUMMARIZE_URL,
        headers=headers,
        json={"inputs": text, "parameters": {"max_length": max_length, "min_length": min_length}}
    )
    # Check if API returned an error
    result = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API error: {result}")
    return result[0]["summary_text"]
def prepare_text_for_summarization(chunks, max_tokens=800):
    combined_text = ""
    token_count = 0

    for chunk in chunks:
        text = chunk['metadata'].get('text', '')
        word_count = len(text.split())
        est_tokens = int(word_count * 1.3)

        if token_count + est_tokens > max_tokens:
            break
        combined_text += " " + text
        token_count += est_tokens

    return combined_text.strip()


def summarize_text(text, max_len=150, min_len=30):
    if not text:
        return "No text available for summarization."
    try:
        return call_summarizer(text, max_length=max_len, min_length=min_len)
    except Exception as e:
        return {"error": f"Summarization failed: {str(e)}"}


def smart_retrieve_and_summarize(
    query: str,
    retriever,
    metadata_filter: Optional[Dict] = None,
    score_threshold: float = 0.75,
    max_tokens: int = 800
) -> Dict:
    results = retriever.get_relevant_documents(query)

    filtered_results = [
        doc for doc in results
        if (not metadata_filter or all(doc.metadata.get(k) == v for k, v in metadata_filter.items()))
        and doc.metadata.get("score", 1) >= score_threshold
    ]

    if not filtered_results:
        return {
            "summary": "No relevant content found.",
            "raw_chunks": [],
            "metadata": []
        }

    combined_text = prepare_text_for_summarization(filtered_results, max_tokens=max_tokens)
    summary = summarize_text(combined_text)

    return {
        "summary": summary,
        "raw_chunks": [doc.page_content for doc in filtered_results],
        "metadata": [doc.metadata for doc in filtered_results]
    }


if __name__ == "__main__":
    response = requests.post(
        HF_SUMMARIZE_URL,
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": "Machine learning enables computers to learn from data."},
        timeout=120
    )
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)