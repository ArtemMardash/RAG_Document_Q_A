# RAG Document Q&A API

A backend API that lets users upload documents and ask questions about them using a full **Retrieval-Augmented Generation (RAG)** pipeline. Built with Python and FastAPI, the system chunks and embeds documents locally, stores vectors in PostgreSQL with pgvector, and generates grounded answers via Groq's LLM API.

The entire stack costs $0 to run.

---

## How it works

**Upload flow:**
```
PDF → Azure Blob Storage → text extraction → chunking → 
local embeddings (sentence-transformers) → pgvector storage
```

**Query flow:**
```
question → embed question → ANN search (top 20 candidates) → 
cross-encoder re-ranking (true top 5) → Groq LLM → grounded answer
```

The LLM only sees the most relevant chunks from the document — not the full file — which keeps responses fast, accurate, and grounded in actual content.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | Python, FastAPI |
| Vector DB | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2, runs locally) |
| Re-ranking | cross-encoder (ms-marco-MiniLM-L-6-v2, runs locally) |
| LLM | Groq API — free tier (Llama 3.1) |
| Object Storage | Azure Blob Storage — free tier |
| Containerization | Docker, Docker Compose |

---

## Project Structure

```
app/
├── api/routes/          # FastAPI route handlers
├── core/                # Database, config, dependencies
├── entities/            # SQLAlchemy ORM models
├── repositories/        # Database access layer
├── schemas/             # Pydantic request/response models
├── services/            # Chunking, embedding, storage, re-ranking, LLM
└── workers/             # Background ingestion pipeline
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- Docker + Docker Compose
- Azure Storage Account (free tier) — [portal.azure.com](https://portal.azure.com)
- Groq API key (free) — [console.groq.com](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/ArtemMardash/RAG_Document_Q_A
cd RAG_Document_Q_A
```

### 2. Set up environment variables
```bash
cp .env.example .env
```

Fill in your `.env`:
```
DATABASE_URL=postgresql://raguser:ragpass@db:5432/ragdb
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CONTAINER_NAME=documents
GROQ_API_KEY=your_key
GROQ_MODEL=llama-3.1-8b-instant
CHUNK_SIZE=512
CHUNK_OVERLAP=64
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

This starts the FastAPI app and PostgreSQL with pgvector. The vector extension, ivfflat index, and all tables are created automatically on startup.

### 4. Run locally (without Docker)
```bash
pip install -r requirements.txt
docker run --name rag-postgres -e POSTGRES_DB=ragdb -e POSTGRES_USER=raguser -e POSTGRES_PASSWORD=ragpass -p 5432:5432 -d pgvector/pgvector:pg16
uvicorn app.main:app --reload
```

Update `DATABASE_URL` in `.env` to use `localhost` instead of `db` when running locally.

---

## API Endpoints

Interactive docs available at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload a PDF, triggers background ingestion |
| `GET` | `/documents/` | List all documents |
| `GET` | `/documents/{id}` | Get document status (`processing` / `ready`) |
| `DELETE` | `/documents/{id}` | Delete document and its chunks |
| `POST` | `/query/` | Ask a question, get a grounded answer |

### Upload a document
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "document_id": 1,
  "file_name": "resume.pdf",
  "status": "processing",
  "message": "File uploaded successfully, processing in background"
}
```

### Query a document
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key skills?"}'
```

Response:
```json
{
  "answer": "Based on the document...",
  "source_chunks": ["chunk 1 text...", "chunk 2 text..."]
}
```

---

## Key Design Decisions

- **Two-stage retrieval** — ANN search via ivfflat index retrieves top 20 candidates fast, cross-encoder re-ranker selects the true top 5 by deeply reading each question-chunk pair
- **Local embeddings and re-ranking** — both sentence-transformers and the cross-encoder run entirely on the host machine, zero API cost and no data leaving your infrastructure
- **No Celery/Redis** — FastAPI's built-in `BackgroundTasks` handles async ingestion cleanly without the overhead of a distributed task queue
- **pgvector over a dedicated vector DB** — keeps the stack simple at this scale; the architecture supports migrating to Pinecone or Qdrant if the dataset grows to millions of chunks
- **Azure Blob Storage** — stores raw files separately from the database, serving them via persistent URLs
