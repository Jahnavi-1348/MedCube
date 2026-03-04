#!/usr/bin/env python
# coding: utf-8

# In[3]:

from dotenv import load_dotenv
load_dotenv()
import requests
import os
import re
from uuid import uuid4
from typing import List, Dict

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

def get_embedding(text: str):
    response = requests.post(
        HF_MODEL_URL,
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": [text]}
    )
    result = response.json()[0]
    if isinstance(result[0], list):
        embedding = result[0]
    else:
        embedding = result
    return embedding


def extract_paragraphs(text: str) -> List[str]:
    cleaned = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    return [p.strip() for p in cleaned.split('\n\n') if p.strip()]





if __name__ == "__main__":
    response = requests.post(
        HF_MODEL_URL,
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": "test"}
    )
    result = response.json()
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text[:300])
    print("DIMENSION:", len(result))