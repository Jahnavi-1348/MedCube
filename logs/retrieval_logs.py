#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import os

# This adds the main MEDCUBE folder to the search path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import csv
from datetime import datetime


from service.indexing import hybrid_search
from service.summarize import prepare_text_for_summarization, summarize_text
from logs.logger import log_interaction

# In[4]:


LOG_FILE = "query_logs.csv"

def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp", 
                "query", 
                "filters", 
                "matched_chunks", 
                "summary", 
                "retrieved_metadata"
            ])


# In[5]:


def log_retrieval(
    query: str,
    results: list,
    metadata_filter: dict = None,
    log_path: str = "logs/retrieval_logs.csv"
):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_exists = os.path.isfile(log_path)

    with open(log_path, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header if not already present
        if not file_exists:
            writer.writerow([
                "timestamp", "query", "filter", "document_id",
                "score", "page_number", "snippet", "source"
            ])

        for match in results:
            metadata = match.get("metadata", {})
            writer.writerow([
                datetime.now().isoformat(),
                query,
                metadata_filter,
                match.get("id", ""),
                round(match.get("score", 0), 4),
                metadata.get("page_number", "N/A"),
                metadata.get("text", "")[:100].replace('\n', ' ') + "...",
                metadata.get("file_name", "N/A")
            ])


# end to end function query> retrieve>summarize
# 
query = input("Ask MedCube: ")
selections = {
    "department": "Cardiology",
    "doctor": "", # User didn't select a doctor
    "medications": "",
    "patient_name": "",
    "issue": "Hypertension"
}
# In[6]
metadata_filter = {k: v for k, v in selections.items() if v}


def retrieve_and_summarize(query, metadata_filter=None, top_k=5):
    
    results = hybrid_search(query=query, metadata_filter=metadata_filter, top_k=top_k)

    if not results:
        return {"summary": "No results found for the query.", "results": []}

    summary_text = prepare_text_for_summarization(results, max_tokens=800)
    summary = summarize_text(summary_text)

    # Return both detailed matches and summary
    return {
        "summary": summary,
        "results": results
    }

response = retrieve_and_summarize(query,metadata_filter)

log_interaction(query=query,metadata_filter=metadata_filter,results= response["results"],summary=response["summary"], timestamp=datetime.now().isoformat())



# In[ ]:


# Example usage:
#init_log_file()

#query = "Patient has persistent cough and shortness of breath"
#filters = {"doctor_name": "Dr. Smith"}

#results = smart_retrieve(query=query, metadata_filter=filters)
#summary = summarizer(" ".join([res.page_content for res in results]), max_length=100)[0]['summary_text']

#log_query(query, filters, results, summary)

#print("Summary:", summary)


