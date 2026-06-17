"""Visualization model — generated visual knowledge representations."""

import uuid

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Visualization(Base, TimestampMixin):
    __tablename__ = "visualizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    viz_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # viz_type values: infographic, mind_map, knowledge_graph, timeline, flowchart, dashboard, decision_tree, learning_path
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    spec: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # spec holds the full visualization definition (nodes, edges, layout, styling)
    theme: Mapped[str] = mapped_column(String(50), default="default")
    version: Mapped[int] = mapped_column(default=1)
    is_published: Mapped[bool] = mapped_column(default=False)
    published_url: Mapped[str | None] = mapped_column(String(500))

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="visualizations")  # noqa: F821
    nodes: Mapped[list["KnowledgeNode"]] = relationship(back_populates="visualization", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Visualization {self.title} ({self.viz_type})>"
