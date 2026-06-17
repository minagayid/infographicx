"""Collaboration Session model — real-time collaborative editing."""

import uuid

from sqlalchemy import String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CollaborationSession(Base, TimestampMixin):
    __tablename__ = "collaboration_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cursor_position: Mapped[dict | None] = mapped_column(JSON)
    viewport: Mapped[dict | None] = mapped_column(JSON)
    selected_elements: Mapped[list | None] = mapped_column(JSON, default=list)
    color: Mapped[str] = mapped_column(String(20), default="#3B82F6")

    def __repr__(self) -> str:
        return f"<CollaborationSession user={self.user_id} project={self.project_id}>"
