from fastapi import APIRouter, Depends
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.schemas.query import QueryRequest, QueryResponse
from app.core.dependencies import get_chunk_repository, get_embedding_service, get_llm_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    query_vector = embedding_service.embed([request.question])[0]
    chunks = chunk_repo.similarity_search(query_vector, top_k=5)
    chunk_texts = [chunk.content for chunk in chunks]
    answer = llm_service.answer(request.question, chunk_texts)

    return QueryResponse(
        answer=answer,
        source_chunks=chunk_texts
    )
