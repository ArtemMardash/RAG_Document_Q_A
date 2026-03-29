from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.core.database import SessionLocal
import pypdf
import io


def ingest_document(document_id: int, file_name: str):
    db = SessionLocal()
    try:
        document_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)
        storage_service = StorageService()
        chunking_service = ChunkingService()
        embedding_service = EmbeddingService()

        # 1. download file from azure
        file_bytes = storage_service.download_file(file_name)

        # 2. extract raw text from pdf
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        raw_text = ""
        for page in pdf_reader.pages:
            raw_text += page.extract_text()

        # 3. chunk the text
        chunks = chunking_service.chunk_text(raw_text)

        # 4. embed the chunks
        embeddings = embedding_service.embed(chunks)

        # 5. store chunks + vectors in postgresql
        chunk_repo.bulk_create(document_id, chunks, embeddings)

        # 6. mark document as ready
        document_repo.mark_ready(document_id)

    except Exception as e:
        document_repo.mark_failed(document_id)
        raise e
    finally:
        db.close()