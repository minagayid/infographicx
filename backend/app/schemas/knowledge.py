"""Knowledge graph schemas — nodes, edges, and full graph."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class KnowledgeNodeRead(BaseModel):
    id: uuid.UUID
    visualization_id: uuid.UUID
    node_type: str
    label: str
    description: str | None
    properties: dict | None
    position_x: float | None
    position_y: float | None
    depth_level: int
    importance_score: float | None
    source_ref: dict | None

    model_config = {"from_attributes": True}


class KnowledgeEdgeRead(BaseModel):
    id: uuid.UUID
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    edge_type: str
    label: str | None
    weight: float
    properties: dict | None
    confidence: float

    model_config = {"from_attributes": True}


class KnowledgeGraphRead(BaseModel):
    """Complete knowledge graph with nodes and edges."""
    visualization_id: uuid.UUID
    nodes: list[KnowledgeNodeRead]
    edges: list[KnowledgeEdgeRead]
