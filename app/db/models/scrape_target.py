from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScrapeTarget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scrape_targets"

    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    seller: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
