"""Knowledge Edge model — relationships between knowledge nodes."""

import uuid

from sqlalchemy import String, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class KnowledgeEdge(Base, TimestampMixin):
    __tablename__ = "knowledge_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_nodes.id"), nullable=False
    )
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # edge_type: depends_on, causes, related_to, contains, precedes, compares, belongs_to
    label: Mapped[str | None] = mapped_column(String(255))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    properties: Mapped[dict | None] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Relationships
    source_node: Mapped["KnowledgeNode"] = relationship(  # noqa: F821
        foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node: Mapped["KnowledgeNode"] = relationship(  # noqa: F821
        foreign_keys=[target_node_id], back_populates="incoming_edges"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeEdge {self.edge_type}: {self.source_node_id} -> {self.target_node_id}>"
