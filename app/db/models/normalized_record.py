import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NormalizedRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "normalized_records"

    raw_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw_artifacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    card_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    set_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    card_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grading_company: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    sold_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    listing_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, unique=True
    )
    raw_title: Mapped[str | None] = mapped_column(Text, nullable=True)
