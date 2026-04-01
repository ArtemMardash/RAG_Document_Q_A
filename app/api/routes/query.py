from fastapi import APIRouter, Depends
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService
from app.schemas.query import QueryRequest, QueryResponse
from app.core.dependencies import get_chunk_repository, get_embedding_service, get_llm_service, get_reranker_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    # stage 1 — embed question
    query_vector = embedding_service.embed([request.question])[0]

    # stage 2 — ANN retrieves top 20 candidates
    candidates = chunk_repo.similarity_search_ann(query_vector, top_k=20)
    chunk_texts = [chunk.content for chunk in candidates]

    # stage 3 — re-ranker picks true top 5
    top_5 = reranker_service.rerank(request.question, chunk_texts, top_k=5)

    # stage 4 — LLM answers
    answer = llm_service.answer(request.question, top_5)

    return QueryResponse(answer=answer, source_chunks=top_5)
