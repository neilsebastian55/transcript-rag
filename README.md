# Transcript Intelligence

A RAG system for asking questions across transcripts — interview recordings, YouTube videos, or any long-form text. Built as a demo for [Great Question](https://greatquestion.co), but the core pipeline works for any research corpus.

**Stack:** FastAPI · ChromaDB · sentence-transformers · Claude (Anthropic) · React + Vite

---

## Features

- **Upload** `.txt`, `.vtt`, `.srt` files or paste raw text
- **YouTube** — paste a URL, get the transcript automatically
- **Semantic retrieval** — sentence-transformers embeddings + ChromaDB vector store
- **Claude synthesis** — retrieved chunks passed to Claude for grounded answers
- **Multi-turn memory** — conversation history preserved across queries
- **Retrieval evals** — built-in eval script with LLM-as-judge scoring
- **Feedback logging** — thumbs up/down per query, written to `feedback.jsonl`
- **CLI** — run queries from the terminal without the UI

---

## Quickstart

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/transcript-rag
cd transcript-rag
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. Docs at `/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## CLI

Query a transcript directly without the UI:

```bash
# From a file
python scripts/query_cli.py path/to/transcript.txt

# From YouTube
python scripts/query_cli.py https://youtube.com/watch?v=VIDEO_ID
```

---

## Evals

Run the eval suite against a transcript:

```bash
python scripts/eval.py path/to/transcript.txt scripts/sample_evals.json
```

Edit `sample_evals.json` with your own question/expected-answer pairs. Results are saved to `eval_results.json`.

---

## Project Structure

```
transcript-rag/
├── backend/
│   ├── main.py          # FastAPI app + routes
│   ├── rag.py           # Chunking, embedding, retrieval, Claude synthesis
│   ├── youtube.py       # YouTube transcript fetcher
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js       # API client
│   │   └── components/
│   │       ├── LoadPanel.jsx
│   │       ├── QueryPanel.jsx
│   │       ├── ResultCard.jsx
│   │       └── CollectionBadge.jsx
│   └── package.json
└── scripts/
    ├── query_cli.py     # Terminal REPL
    ├── eval.py          # Eval runner with LLM-as-judge
    └── sample_evals.json
```

---

## How It Works

1. **Chunking** — transcript split into 400-word chunks with 80-word overlap
2. **Embedding** — each chunk embedded with `all-MiniLM-L6-v2` (runs locally)
3. **Storage** — embeddings stored in ChromaDB (in-memory, no setup needed)
4. **Retrieval** — cosine similarity search returns top-k chunks for each query
5. **Synthesis** — chunks passed to Claude with the question; answer grounded in context
6. **Feedback** — user ratings written to `feedback.jsonl` for offline analysis

---

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required. Get one at [console.anthropic.com](https://console.anthropic.com) |

---

## License

MIT
