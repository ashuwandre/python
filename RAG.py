"""
RAG application

Pipeline:
1. Load text files from the data folder
2. Split each file into chunks
3. Store the chunks in a persistent Chroma database
4. Retrieve the chunks that match a question
5. Call an LLM to generate the answer

Install:
pip install chromadb langchain-openai

The vector store uses Chroma's local embedding model, so indexing works
without an API key. The answer step calls OpenAI, so set a key first:

PowerShell:
    $env:OPENAI_API_KEY = "your-key"

Run:
    python RAG.py
    python RAG.py "What is a tuple in Python?"
"""

import os
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "study_notes"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 3


def load_documents(data_dir):
    """Read every .txt file in the data folder."""
    paths = sorted(data_dir.glob("*.txt"))
    if not paths:
        raise FileNotFoundError(f"No text files found in {data_dir}")

    documents = []
    for path in paths:
        documents.append(
            {
                "source": path.name,
                "text": path.read_text(encoding="utf-8").strip(),
            }
        )
    return documents


def split_long_paragraph(paragraph, chunk_size, overlap):
    """Break one long paragraph on spaces, keeping a small overlap."""
    words = paragraph.split()
    chunks = []
    start = 0
    while start < len(words):
        piece = []
        length = 0
        index = start
        while index < len(words) and length + len(words[index]) + 1 <= chunk_size:
            piece.append(words[index])
            length += len(words[index]) + 1
            index += 1
        if not piece:
            piece = [words[start]]
            index = start + 1
        chunks.append(" ".join(piece))
        if index >= len(words):
            break
        overlap_words = max(1, overlap // 8)
        start = max(index - overlap_words, start + 1)
    return chunks


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split one document on paragraphs, then pack them into chunks."""
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(split_long_paragraph(paragraph, chunk_size, overlap))
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)
    return chunks


def split_documents(documents):
    """Turn loaded files into chunks with a stable id and source name."""
    chunks = []
    for document in documents:
        pieces = split_text(document["text"])
        for index, piece in enumerate(pieces):
            chunks.append(
                {
                    "id": f"{document['source']}-{index}",
                    "text": piece,
                    "source": document["source"],
                }
            )
    return chunks


def get_collection():
    """Open the same on-disk Chroma collection every time this script runs."""
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    embedding = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(chunks):
    """Upsert chunks so the database stays on disk and can be queried later."""
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[{"source": chunk["source"]} for chunk in chunks],
    )

    current_ids = {chunk["id"] for chunk in chunks}
    stored_ids = collection.get()["ids"]
    stale_ids = [item_id for item_id in stored_ids if item_id not in current_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)
    return collection


def retrieve(collection, question, top_k=TOP_K):
    """Return the closest stored chunks for this question."""
    result = collection.query(query_texts=[question], n_results=top_k)
    matches = []
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    for text, meta, distance in zip(documents, metadatas, distances):
        matches.append(
            {
                "text": text,
                "source": meta["source"],
                "distance": distance,
            }
        )
    return matches


def build_context(matches):
    parts = []
    for number, match in enumerate(matches, start=1):
        parts.append(f"[{number}] ({match['source']}) {match['text']}")
    return "\n\n".join(parts)


def generate_answer(question, context):
    """LLM call: generate an answer from the retrieved context only."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Retrieval is done, but the LLM call needs a key.\n"
            'PowerShell: $env:OPENAI_API_KEY = "your-key"'
        )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You answer questions about the user's study notes. "
                    "Use only the context below. "
                    "If the context does not contain the answer, say you do not know.\n\n"
                    f"Context:\n{context}"
                )
            ),
            HumanMessage(content=question),
        ]
    )
    return response.content


def main():
    question = "What is a tuple in Python?"
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

    documents = load_documents(DATA_DIR)
    chunks = split_documents(documents)
    collection = store_chunks(chunks)
    matches = retrieve(collection, question)

    print(f"Question: {question}")
    print(f"Stored chunks in persistent Chroma: {collection.count()}")
    print(f"Database path: {CHROMA_DIR}\n")
    print("Retrieved chunks:")
    for match in matches:
        print(f"- {match['source']} (distance {match['distance']:.3f})")
        print(f"  {match['text']}\n")

    context = build_context(matches)
    try:
        answer = generate_answer(question, context)
    except RuntimeError as error:
        print(error)
        return
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
