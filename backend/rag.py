import uuid
import json
import time
from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic

CHUNK_SIZE = 400       # words per chunk
OVERLAP = 80           # word overlap between chunks
EMBED_MODEL = "all-MiniLM-L6-v2"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
FEEDBACK_LOG = Path("feedback.jsonl")


class RAGEngine:
    def __init__(self):
        self.chroma = chromadb.Client()
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.anthropic = Anthropic()
        self.collections: dict[str, dict] = {}

    # ── Loading ──────────────────────────────────────────────────────────────

    def load(self, text: str, source: str) -> dict:
        collection_id = str(uuid.uuid4())[:8]
        chunks = self._chunk(text)

        collection = self.chroma.create_collection(collection_id)
        embeddings = self.embedder.encode([c["text"] for c in chunks]).tolist()

        collection.add(
            documents=[c["text"] for c in chunks],
            embeddings=embeddings,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"start_word": c["start_word"], "index": i} for i, c in enumerate(chunks)],
        )

        word_count = len(text.split())
        self.collections[collection_id] = {
            "id": collection_id,
            "source": source,
            "word_count": word_count,
            "chunk_count": len(chunks),
            "created_at": time.time(),
            "collection": collection,
        }

        return {
            "collection_id": collection_id,
            "source": source,
            "word_count": word_count,
            "chunk_count": len(chunks),
        }

    # ── Querying ─────────────────────────────────────────────────────────────

    def query(self, question: str, collection_id: str, top_k: int = 3, history: list = []) -> dict:
        meta = self.collections[collection_id]
        collection = meta["collection"]

        q_embedding = self.embedder.encode([question]).tolist()
        results = collection.query(query_embeddings=q_embedding, n_results=top_k)

        docs = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        # Convert distances to 0-1 relevance scores
        max_dist = max(distances) if distances else 1
        relevance_scores = [round(1 - (d / (max_dist + 1e-8)), 3) for d in distances]

        context = "\n\n".join(
            f"[Chunk {i+1} — relevance {relevance_scores[i]:.0%}]:\n{doc}"
            for i, doc in enumerate(docs)
        )

        system = (
            "You are a research analyst helping users extract insights from transcripts. "
            "Answer questions using ONLY the provided context chunks. "
            "Be specific and note which chunk supports each claim. "
            "If the context does not contain enough information, say so clearly. "
            "Format answers in plain prose — no bullet spam."
        )

        messages = [
            *history[-6:],  # keep last 3 turns for context
            {
                "role": "user",
                "content": f"Transcript context:\n{context}\n\nQuestion: {question}",
            },
        ]

        response = self.anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=system,
            messages=messages,
        )

        answer = response.content[0].text
        query_id = str(uuid.uuid4())[:8]

        return {
            "query_id": query_id,
            "answer": answer,
            "chunks": [
                {
                    "text": doc,
                    "relevance": relevance_scores[i],
                    "index": metadatas[i]["index"],
                }
                for i, doc in enumerate(docs)
            ],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    # ── Feedback ─────────────────────────────────────────────────────────────

    def log_feedback(self, query_id: str, rating: str, collection_id: str):
        entry = {
            "query_id": query_id,
            "rating": rating,
            "collection_id": collection_id,
            "timestamp": time.time(),
        }
        with open(FEEDBACK_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_feedback_stats(self) -> dict:
        if not FEEDBACK_LOG.exists():
            return {"total": 0, "good": 0, "bad": 0, "score": None}
        entries = [json.loads(l) for l in FEEDBACK_LOG.read_text().splitlines() if l]
        good = sum(1 for e in entries if e["rating"] == "good")
        bad = sum(1 for e in entries if e["rating"] == "bad")
        total = good + bad
        return {
            "total": total,
            "good": good,
            "bad": bad,
            "score": round(good / total, 3) if total else None,
        }

    # ── Collections ──────────────────────────────────────────────────────────

    def list_collections(self) -> list:
        return [
            {
                "id": v["id"],
                "source": v["source"],
                "word_count": v["word_count"],
                "chunk_count": v["chunk_count"],
                "created_at": v["created_at"],
            }
            for v in self.collections.values()
        ]

    def delete_collection(self, collection_id: str):
        if collection_id in self.collections:
            self.chroma.delete_collection(collection_id)
            del self.collections[collection_id]

    # ── Chunking ─────────────────────────────────────────────────────────────

    def _chunk(self, text: str) -> list[dict]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + CHUNK_SIZE]
            chunks.append({"text": " ".join(chunk_words), "start_word": i})
            i += CHUNK_SIZE - OVERLAP
        return chunks
