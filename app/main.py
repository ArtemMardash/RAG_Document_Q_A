from fastapi import FastAPI
from app.api.routes import documents, query
from app.core.database import Base, engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Document QA")

app.include_router(documents.router)
app.include_router(query.router)
