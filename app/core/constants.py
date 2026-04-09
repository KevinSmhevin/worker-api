from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class Source(StrEnum):
    EBAY = "ebay"
    HERITAGE = "heritage"
    GOLDIN = "goldin"


TASK_NAMES = {
    "scrape_ebay_sold": "workers.tasks.ebay.scrape_ebay_sold_listings",
    "health_ping": "workers.tasks.health.ping",
    "cleanup": "workers.tasks.cleanup.cleanup_old_runs",
}

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 60
DEFAULT_RETRY_JITTER = True

MAX_RETRIES_BY_TASK: dict[str, int] = {
    "scrape_ebay_sold": 3,
    "health_ping": 1,
    "cleanup": 2,
}
