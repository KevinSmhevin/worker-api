from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    source: str
    url: str
    seller: str | None = None
    options: dict | None = None
