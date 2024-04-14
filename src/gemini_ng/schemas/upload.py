import mimetypes

from pydantic import Field, HttpUrl

from .base import BaseModel
from .part import FilePart, FilePartData


class UploadFile(BaseModel):
    file_path: str = Field(..., description="Path to the file.")

    mime_type: str | None = Field(None, description="MIME type of the file.")

    body: dict | None = Field(None, description="The body of the request.")

    @classmethod
    def from_path(cls, file_path: str, body: dict | None = None) -> "UploadFile":
        mine_type, _ = mimetypes.guess_type(file_path)
        return cls(file_path=file_path, mime_type=mine_type, body=body)


class UploadedFile(BaseModel):
    name: str = Field(..., description="Unique identifier for the file.")

    display_name: str | None = Field(
        None, alias="displayName", description="Human-readable name for the file."
    )

    mime_type: str | None = Field(..., alias="mimeType", description="MIME type of the file.")

    size_bytes: int = Field(..., alias="sizeBytes", description="Size of the file in bytes.")

    create_time: str = Field(..., alias="createTime", description="Time the file was created.")

    update_time: str = Field(..., alias="updateTime", description="Time the file was updated.")

    expiration_time: str | None = Field(
        None, alias="expirationTime", description="Time the file will expire."
    )

    sha256_hash: str = Field(..., alias="sha256Hash", description="SHA-256 hash of the file.")

    uri: HttpUrl = Field(..., description="URI of the file.")

    def to_file_part(self):
        return FilePart(file_data=FilePartData(file_uri=str(self.uri), mime_type=self.mime_type))
