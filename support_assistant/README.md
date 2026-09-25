# Zepto Support Assistant

## Overview

This module implements a RAG-based customer support assistant for Zepto policy questions.

The assistant uses:
- Local Sentence Transformers for embeddings
- ChromaDB for vector storage and retrieval
- LangGraph for workflow orchestration
- Pydantic for structured responses
- FastAPI for the API
- A deterministic mock mode for reproducible grading without external API calls

---

## Architecture

The overall data flow is:

```text
Policy Documents
       ↓
Document Ingestion
       ↓
Sentence Transformer Embeddings
       ↓
ChromaDB Vector Store
       ↓
User Query
       ↓
LangGraph Intent Classification
       ↓
 ┌───────────────────────┐
 │                       │
Policy Question      General Question
 │                       │
 ↓                       ↓
Retrieve Top 3       Direct Answer
from ChromaDB
 │
 ↓
Generate Answer
 │
 └───────────┬───────────┘
             ↓
       Pydantic Response
             ↓
           FastAPI