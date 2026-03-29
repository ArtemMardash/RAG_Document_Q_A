from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.entities.chunk import Chunk, EMBEDDING_DIMENSIONS


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, document_id: int, chunks: list[str], embeddings: list[list[float]]) -> None:
        chunk_objects = [
            Chunk(
                document_id=document_id,
                content=chunk,
                embedding=embedding,
                chunk_index=index
            )
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        self.db.bulk_save_objects(chunk_objects)
        self.db.commit()

    def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[tuple]:
        return self.db.execute(
            text("""
                 SELECT id, document_id, content, chunk_index
                 FROM chunks
                 ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
                 """),
            {"embedding": str(query_embedding), "top_k": top_k}
        ).fetchall()

    def get_by_document_id(self, document_id: int) -> list[Chunk]:
        return self.db.query(Chunk).filter(Chunk.document_id == document_id).all()

    def delete_by_document_id(self, document_id: int) -> None:
        self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        self.db.commit()