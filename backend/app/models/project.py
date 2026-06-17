"""Project model — top-level container for visualization work."""

import uuid

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, processing, ready, published
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")  # noqa: F821
    sources: Mapped[list["Source"]] = relationship(back_populates="project", lazy="selectin")  # noqa: F821
    visualizations: Mapped[list["Visualization"]] = relationship(back_populates="project", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
