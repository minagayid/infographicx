"""Visualization schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VisualizationSpec(BaseModel):
    """The full specification for a visualization — nodes, edges, layout, styling."""
    nodes: list[dict]
    edges: list[dict]
    layout: dict | None = None
    styling: dict | None = None
    viewport: dict | None = None


class VisualizationCreate(BaseModel):
    viz_type: str = Field(
        pattern=r"^(infographic|mind_map|knowledge_graph|timeline|flowchart|dashboard|decision_tree|learning_path)$"
    )
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    spec: VisualizationSpec
    theme: str = "default"


class VisualizationRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    viz_type: str
    title: str
    description: str | None
    spec: dict
    theme: str
    version: int
    is_published: bool
    published_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
