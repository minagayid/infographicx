"""Source model — input data sources attached to a project."""

import uuid

from sqlalchemy import String, Text, ForeignKey, JSON, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # source_type values: pdf, docx, pptx, csv, xlsx, video, audio, git_repo, website, research_paper, api, database
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    url: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")
    # pending, extracting, extracted, failed
    extraction_result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="sources")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Source {self.name} ({self.source_type})>"
