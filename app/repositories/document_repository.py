from sqlalchemy.orm import Session
from app.core.entities.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, file_name: str, blob_url: str) -> Document:
        document = Document(file_name=file_name, blob_url=blob_url)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_all(self) -> list[Document]:
        return self.db.query(Document).all()

    def mark_ready(self, document_id: int) -> None:
        document = self.get_by_id(document_id)
        document.status = DocumentStatus.READY
        self.db.commit()

    def mark_failed(self, document_id: int) -> None:
        document = self.get_by_id(document_id)
        document.status = DocumentStatus.FAILED
        self.db.commit()

    def delete(self, document_id: int) -> None:
        document = self.get_by_id(document_id)
        self.db.delete(document)
        self.db.commit()