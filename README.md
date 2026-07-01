# MedCube 🏥

An AI-powered Retrieval-Augmented Generation (RAG) application that enables healthcare professionals to quickly retrieve relevant information from medical documents using natural language search instead of manually browsing through files.

---

## Overview

Medical records often contain hundreds of pages of patient reports, prescriptions, discharge summaries, and clinical notes. Finding specific information manually is time-consuming and inefficient.

MedCube indexes uploaded medical documents into a vector database, allowing users to ask questions in plain English and instantly retrieve the most relevant document sections along with an AI-generated summary.

---

## Problem Statement

Traditional document search relies on exact keyword matching, making it difficult to locate information when different terminology is used. As document collections grow, manual searching becomes increasingly inefficient.

MedCube addresses this by using semantic search, understanding the meaning of a query rather than matching exact words.

---

## Solution

The application follows a Retrieval-Augmented Generation (RAG) pipeline:

1. Upload PDF or TXT documents.
2. Extract and split text into overlapping chunks.
3. Generate embeddings using HuggingFace MiniLM.
4. Store embeddings in Pinecone.
5. Convert user queries into embeddings.
6. Retrieve the most relevant document chunks through vector similarity search.
7. Apply metadata filters and generate an AI summary using DistilBART.
8. Display the retrieved content with source document and page information.

---

## Features

### Authentication & Security

* JWT-based authentication
* Role-based access (Admin & Doctor)
* Password hashing with bcrypt
* Token expiration (60 minutes)
* Rate limiting
* Protected API routes

### User Management

* Admin creates and manages doctor accounts
* User activation/deactivation
* Role-based permissions

### Document Processing

* PDF and TXT upload support
* Duplicate file detection
* Secure file validation
* Automatic chunking with overlap
* Vector indexing in Pinecone

### Intelligent Retrieval

* Natural language search
* Semantic vector search
* Metadata filtering (department, doctor, patient, issue, medication)
* AI-generated summaries
* Source file and page references

### Logging

* JSONL interaction logs
* CSV audit logs
* Retrieval performance tracking

---

## System Architecture

```text
          Upload Document
                 │
                 ▼
      Text Extraction & Chunking
                 │
                 ▼
   HuggingFace MiniLM Embeddings
                 │
                 ▼
      Pinecone Vector Database
                 │
────────────────────────────────────
                 ▲
            User Query
                 │
                 ▼
        Query Embedding
                 │
                 ▼
      Vector Similarity Search
                 │
                 ▼
        Metadata Filtering
                 │
                 ▼
      DistilBART Summarization
                 │
                 ▼
     Relevant Results + Sources
```

---

## Tech Stack

**Backend**

* Python
* FastAPI

**Machine Learning**

* HuggingFace Sentence Transformers (MiniLM)
* DistilBART

**Vector Database**

* Pinecone

**Authentication**

* JWT
* bcrypt

**Frontend**

* HTML
* CSS

---

## License

This project is intended for educational and portfolio purposes. It demonstrates Retrieval-Augmented Generation (RAG) techniques for intelligent medical document retrieval and is not intended for clinical or diagnostic use.
