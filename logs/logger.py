#!/usr/bin/env python
# coding: utf-8

# In[5]:


import json
from datetime import datetime
from pathlib import Path
import portalocker
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)



# In[6]:


def log_interaction(
    query: str,
    retrieved_chunks: list,
    summary: str,
    metadata: dict = None,
    save_full_chunks: bool = False,
    verbose: bool = False):
    if save_full_chunks:
        chunks = [
            {
                "id": chunk.get("id"),
                "content": chunk.get("content", "N/A")
            }
            for chunk in retrieved_chunks
        ]
    else:
        chunks = [chunk.get("id") for chunk in retrieved_chunks]

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "metadata_filter": metadata or {},
        "retrieved_chunks": chunks,
        "summary": summary
    }

    log_file = LOG_DIR / f"log_{datetime.now().date()}.jsonl"
    with portalocker.Lock(log_file, "a") as f:
        f.write(json.dumps(log_data) + "\n")

    if verbose:
        print("\n Interaction Log:")
        print(json.dumps(log_data, indent=2))





