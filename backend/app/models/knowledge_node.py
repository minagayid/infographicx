"""Knowledge Node model — individual knowledge elements in a visualization."""

import uuid

from sqlalchemy import String, Text, ForeignKey, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class KnowledgeNode(Base, TimestampMixin):
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visualization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("visualizations.id"), nullable=False
    )
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # node_type: entity, process, event, metric, concept, decision, layer
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    properties: Mapped[dict | None] = mapped_column(JSON, default=dict)
    position_x: Mapped[float | None] = mapped_column(Float)
    position_y: Mapped[float | None] = mapped_column(Float)
    depth_level: Mapped[int] = mapped_column(Integer, default=0)
    importance_score: Mapped[float | None] = mapped_column(Float)
    source_ref: Mapped[dict | None] = mapped_column(JSON)
    # source_ref links back to the original source + location

    # Relationships
    visualization: Mapped["Visualization"] = relationship(back_populates="nodes")  # noqa: F821
    outgoing_edges: Mapped[list["KnowledgeEdge"]] = relationship(  # noqa: F821
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.source_node_id",
        back_populates="source_node",
    )
    incoming_edges: Mapped[list["KnowledgeEdge"]] = relationship(  # noqa: F821
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.target_node_id",
        back_populates="target_node",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeNode {self.label} ({self.node_type})>"
