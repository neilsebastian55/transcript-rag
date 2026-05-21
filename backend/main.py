from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .rag import RAGEngine
from .youtube import fetch_youtube_transcript

app = FastAPI(title="Transcript RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()


class QueryRequest(BaseModel):
    question: str
    collection_id: str
    top_k: int = 3
    history: Optional[list] = []


class YoutubeRequest(BaseModel):
    url: str


class FeedbackRequest(BaseModel):
    query_id: str
    rating: str  # "good" | "bad"
    collection_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcripts/upload")
async def upload_transcript(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    if not text.strip():
        raise HTTPException(400, "File is empty")
    result = rag.load(text, source=file.filename)
    return result


@app.post("/transcripts/youtube")
async def load_youtube(req: YoutubeRequest):
    try:
        text, title = fetch_youtube_transcript(req.url)
    except Exception as e:
        raise HTTPException(400, f"Could not fetch transcript: {e}")
    result = rag.load(text, source=title)
    return result


@app.post("/transcripts/text")
async def load_text(body: dict):
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(400, "text field required")
    result = rag.load(text, source=body.get("source", "pasted text"))
    return result


@app.post("/query")
async def query(req: QueryRequest):
    if req.collection_id not in rag.collections:
        raise HTTPException(404, "Collection not found. Load a transcript first.")
    result = rag.query(
        question=req.question,
        collection_id=req.collection_id,
        top_k=req.top_k,
        history=req.history or [],
    )
    return result


@app.post("/feedback")
async def feedback(req: FeedbackRequest):
    rag.log_feedback(req.query_id, req.rating, req.collection_id)
    return {"status": "logged"}


@app.get("/collections")
def list_collections():
    return {"collections": rag.list_collections()}


@app.delete("/collections/{collection_id}")
def delete_collection(collection_id: str):
    rag.delete_collection(collection_id)
    return {"status": "deleted"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
