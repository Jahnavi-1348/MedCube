#!/usr/bin/env python
# coding: utf-8

# In[13]:


import fitz  # PyMuPDF
import re
import nltk
from datetime import datetime
from typing import List, Dict


# In[14]:


nltk.download('punkt')
from nltk.tokenize import word_tokenize


# In[15]:


def extract_paragraphs(text: str) -> List[str]:
    import re
    # Collapse lines that are likely part of same paragraph
    cleaned = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    return [p.strip() for p in cleaned.split('\n\n') if p.strip()]


# In[16]:


def create_chunks_with_metadata(paragraphs: List[str], page_num: int, chunk_size: int = 512, overlap: int = 20) -> List[Dict]:
    chunks = []
    buffer = []
    buffer_len = 0

    for para in paragraphs:
        tokens = word_tokenize(para)

        if buffer_len + len(tokens) > chunk_size:
            chunk_text = " ".join(buffer)
            metadata = extract_metadata(chunk_text, page_num)
            chunks.append({"text": chunk_text, "metadata": metadata})
            buffer = buffer[-overlap:] + tokens
            buffer_len = len(buffer)
        else:
            buffer += tokens
            buffer_len += len(tokens)

    if buffer:
        chunk_text = " ".join(buffer)
        metadata = extract_metadata(chunk_text, page_num)
        chunks.append({"text": chunk_text, "metadata": metadata})

    return chunks


# In[17]:


# Extract metadata using regex
def extract_metadata(text: str, page_num: int) -> Dict:
    metadata = {
        "page_number": page_num,
        "upload_date": datetime.now().isoformat()
    }
 ### check on what the patterns could do and imapct 
    patterns = {
        "patient_name": r"(?:Patient\s+Name|Name of Patient)[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        "doctor": r"(?:Doctor|Physician|Attending Dr\.?)[:\-]?\s*(Dr\.?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        "medications": r"(?:Medications|Prescribed|Drugs Given)[:\-]?\s*(.+?)(?:\n|$)",
        "department": r"(?:Department|Unit)[:\-]?\s*([A-Za-z &]+)",
        "issue": r"(?:Diagnosis|Issue|Concern)[:\-]?\s*(.+?)(?:\n|$)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


# In[ ]:




