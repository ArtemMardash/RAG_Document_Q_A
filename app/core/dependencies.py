from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.services.llm_service import LLMService
from app.services.reranker_service import RerankerService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_chunk_repository(db: Session = Depends(get_db)) -> ChunkRepository:
    return ChunkRepository(db)


def get_chunking_service() -> ChunkingService:
    return ChunkingService()

_embedding_service = EmbeddingService()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_storage_service() -> StorageService:
    return StorageService()

_llm_service = LLMService()
def get_llm_service() -> LLMService:
    return LLMService()

_reranker_service = RerankerService()
def get_reranker_service() -> RerankerService:
    return _reranker_service