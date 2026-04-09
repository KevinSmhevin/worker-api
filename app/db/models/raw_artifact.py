import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RawArtifact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "raw_artifacts"

    task_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, unique=True
    )
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
