from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"


def load_documents():
    """Read all 8 Zepto policy documents."""

    documents = []

    for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        documents.append(
            {
                "id": file_path.stem,
                "text": text,
                "source": file_path.name,
            }
        )

    return documents


def build_vector_store():
    """Create embeddings and store them in ChromaDB."""

    documents = load_documents()

    # Make sure all 8 required documents exist
    if len(documents) != 8:
        raise ValueError(
            f"Expected 8 policy documents, but found {len(documents)}."
        )

    print("Loading embedding model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create persistent ChromaDB database
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Extract document information
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]

    # Generate embeddings locally
    embeddings = model.encode(texts).tolist()

    # Store documents and embeddings
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {"source": doc["source"]}
            for doc in documents
        ],
    )

    print(f"Successfully stored {len(documents)} documents in ChromaDB.")


if __name__ == "__main__":
    build_vector_store()