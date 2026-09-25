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

## Testing Status

The support assistant was tested locally using FastAPI with `MOCK_LLM=1`.
Both policy retrieval and general-question routing were verified through the `/ask` endpoint.
Example request and response JSON transcripts are available in `transcripts.md`.