from pydantic import BaseModel


class RawRecord(BaseModel):
    """Unstructured listing data extracted from a scrape, before normalization."""

    title: str
    price: str | None = None
    sold_date: str | None = None
    listing_url: str | None = None
    image_url: str | None = None
    seller: str | None = None
    source: str = ""
    extra: dict | None = None
