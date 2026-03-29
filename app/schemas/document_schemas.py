from pydantic import BaseModel
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: int
    file_name: str
    status: str
    message: str


class DocumentOut(BaseModel):
    id: int
    file_name: str
    blob_url: str
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True