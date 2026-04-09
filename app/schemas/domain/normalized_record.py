from datetime import datetime

from pydantic import BaseModel


class NormalizedRecordSchema(BaseModel):
    """Structured card data after parsing and normalization."""

    card_name: str | None = None
    set_name: str | None = None
    card_number: str | None = None
    grading_company: str | None = None
    grade: str | None = None
    price: float | None = None
    currency: str = "USD"
    sold_date: datetime | None = None
    listing_url: str | None = None
    image_url: str | None = None
    source: str = ""
    content_hash: str = ""
    raw_title: str | None = None
