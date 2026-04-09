"""Placeholder for OpenTelemetry tracing.

Will be implemented when opentelemetry SDK is added as a dependency.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


def init_tracing() -> None:
    logger.info("tracing_noop", reason="OpenTelemetry not yet configured")
