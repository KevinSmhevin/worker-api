"""Placeholder for Prometheus metrics.

Will be implemented when prometheus_client is added as a dependency.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


def record_scrape_duration(source: str, duration_seconds: float) -> None:
    logger.info("metric_scrape_duration", source=source, duration=duration_seconds)


def record_items_scraped(source: str, count: int) -> None:
    logger.info("metric_items_scraped", source=source, count=count)


def record_task_outcome(task_name: str, outcome: str) -> None:
    logger.info("metric_task_outcome", task_name=task_name, outcome=outcome)
