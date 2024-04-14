from pydantic import Field

from .base import BaseModel


class TextPart(BaseModel):
    text: str = Field(..., description="Text content.")


class FilePartData(BaseModel):
    file_uri: str = Field(..., alias="fileUri", description="URI of the file.")
    mime_type: str = Field(..., alias="mimeType", description="MIME type of the file.")


class FilePart(BaseModel):
    file_data: FilePartData = Field(..., description="URL of the file.")


class ImagePart(FilePart):
    ...


class VideoPart(BaseModel):
    time_spans: list[TextPart] = Field(..., description="Time spans of the video.")

    frames: list[ImagePart | FilePart] = Field(..., description="Frames of the video.")

    def content_parts(self) -> list[TextPart | ImagePart | FilePart]:
        parts = []

        for span, frame in zip(self.time_spans, self.frames):
            parts.append(span)
            parts.append(frame)

        return parts
