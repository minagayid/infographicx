"""Source schemas — input data source management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    source_type: str = Field(
        pattern=r"^(pdf|docx|pptx|csv|xlsx|video|audio|git_repo|website|research_paper|api|database)$"
    )
    name: str = Field(min_length=1, max_length=255)
    url: str | None = None
    metadata: dict | None = None


class SourceRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    source_type: str
    name: str
    file_path: str | None
    file_size: int | None
    mime_type: str | None
    url: str | None
    metadata_json: dict | None
    processing_status: str
    extraction_result: dict | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceProcessRequest(BaseModel):
    """Request to trigger processing of a source."""
    source_ids: list[uuid.UUID]
    options: dict | None = None
