import uuid

from pydantic import BaseModel


class ScrapeTaskPayload(BaseModel):
    job_id: uuid.UUID
    source: str
    url: str
    seller: str | None = None
    options: dict | None = None


class CleanupTaskPayload(BaseModel):
    older_than_days: int = 30


class ReprocessTaskPayload(BaseModel):
    job_id: uuid.UUID
    force: bool = False
