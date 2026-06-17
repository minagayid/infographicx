"""Project schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    settings: dict | None = None


class ProjectRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    settings: dict | None
    thumbnail_url: str | None
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    settings: dict | None = None
