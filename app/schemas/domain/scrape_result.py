from pydantic import BaseModel

from app.schemas.domain.raw_record import RawRecord


class ScrapeResult(BaseModel):
    raw_html: str | None = None
    items: list[RawRecord] = []
    total_items: int = 0
    pages_scraped: int = 1
    metadata: dict | None = None
