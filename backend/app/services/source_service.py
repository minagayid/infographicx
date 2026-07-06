"""Source service — persist uploaded files and register them as sources."""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.source import Source

# Map a file extension to the Source.source_type vocabulary.
_EXT_TO_TYPE = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".pptx": "pptx",
    ".ppt": "pptx",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".mp4": "video",
    ".mov": "video",
    ".mp3": "audio",
    ".wav": "audio",
}


class SourceService:
    """Handles file uploads and Source row creation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)

    @staticmethod
    def detect_source_type(filename: str) -> str:
        return _EXT_TO_TYPE.get(Path(filename).suffix.lower(), "pdf")

    async def upload_file(self, project_id: uuid.UUID, file: UploadFile) -> Source:
        """Store the uploaded file on disk and create a Source record."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        source_id = uuid.uuid4()
        filename = file.filename or f"{source_id}"
        dest = self.upload_dir / f"{source_id}_{Path(filename).name}"

        contents = await file.read()
        dest.write_bytes(contents)

        source = Source(
            id=source_id,
            project_id=project_id,
            source_type=self.detect_source_type(filename),
            name=Path(filename).name,
            file_path=str(dest),
            file_size=len(contents),
            mime_type=file.content_type,
            processing_status="pending",
        )
        self.db.add(source)
        await self.db.flush()
        await self.db.refresh(source)
        return source
