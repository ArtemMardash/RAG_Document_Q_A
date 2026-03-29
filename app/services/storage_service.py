from azure.storage.blob import BlobServiceClient
from app.core.config import AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME



class StorageService:
    def __init__(self):
        self.client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        self.container = self.client.get_container_client(AZURE_CONTAINER_NAME)

    def upload_file(self, file_name: str, file_bytes: bytes) -> str:
        blob_client = self.container.get_blob_client(file_name)
        blob_client.upload_blob(file_bytes, overwrite=True)
        return blob_client.url

    def download_file(self, file_name: str) -> bytes:
        blob_client = self.container.get_blob_client(file_name)
        return blob_client.download_blob().readall()

    def delete_file(self, file_name: str) -> None:
        blob_client = self.container.get_blob_client(file_name)
        blob_client.delete_blob()