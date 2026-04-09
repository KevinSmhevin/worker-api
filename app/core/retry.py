import random

from app.core.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    MAX_RETRIES_BY_TASK,
)


def calculate_backoff(
    attempt: int,
    base_delay: float = DEFAULT_RETRY_BACKOFF,
    jitter: bool = True,
    max_delay: float = 600.0,
) -> float:
    """Exponential backoff with optional jitter.

    Returns delay in seconds: min(base * 2^attempt + jitter, max_delay).
    """
    delay = min(base_delay * (2**attempt), max_delay)
    if jitter:
        delay += random.uniform(0, delay * 0.25)
    return float(delay)


def get_max_retries(task_name: str) -> int:
    return MAX_RETRIES_BY_TASK.get(task_name, DEFAULT_MAX_RETRIES)


def get_celery_retry_kwargs(task_name: str) -> dict:
    """Return kwargs suitable for Celery task retry configuration."""
    return {
        "max_retries": get_max_retries(task_name),
        "retry_backoff": True,
        "retry_backoff_max": 600,
        "retry_jitter": True,
    }
