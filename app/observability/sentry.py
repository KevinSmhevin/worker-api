from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_sentry() -> None:
    """Initialize Sentry SDK if DSN is configured."""
    settings = get_settings()
    if not settings.sentry_dsn:
        logger.info("sentry_disabled", reason="no DSN configured")
        return

    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.1 if settings.is_production else 1.0,
        integrations=[
            CeleryIntegration(),
            SqlalchemyIntegration(),
        ],
    )
    logger.info("sentry_initialized", environment=settings.app_env)
