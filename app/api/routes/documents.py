from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService
from app.workers.ingestion_worker import ingest_document
from app.schemas.document_schemas import DocumentUploadResponse, DocumentOut
from app.core.dependencies import get_document_repository, get_storage_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage_service: StorageService = Depends(get_storage_service)
):
    file_bytes = await file.read()
    blob_url = storage_service.upload_file(file.filename, file_bytes)
    document = document_repo.create(file.filename, blob_url)
    background_tasks.add_task(ingest_document, document.id, file.filename)

    return DocumentUploadResponse(
        document_id=document.id,
        file_name=document.file_name,
        status=document.status,
        message="File uploaded successfully, processing in background"
    )


@router.get("/", response_model=list[DocumentOut])
def get_documents(document_repo: DocumentRepository = Depends(get_document_repository)):
    return document_repo.get_all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    document_repo: DocumentRepository = Depends(get_document_repository)
):
    return document_repo.get_by_id(document_id)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage_service: StorageService = Depends(get_storage_service)
):
    document = document_repo.get_by_id(document_id)
    storage_service.delete_file(document.file_name)
    document_repo.delete(document_id)