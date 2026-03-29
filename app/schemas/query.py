from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    document_id: int | None = None


class QueryResponse(BaseModel):
    answer: str
    source_chunks: list[str]