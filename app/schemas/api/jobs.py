import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.constants import JobStatus


class JobCreate(BaseModel):
    type: str
    payload: dict | None = None


class TaskRunResponse(BaseModel):
    id: uuid.UUID
    task_name: str
    status: str
    attempt: int
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: uuid.UUID
    type: str
    status: JobStatus
    payload: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    task_runs: list[TaskRunResponse] = []

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
