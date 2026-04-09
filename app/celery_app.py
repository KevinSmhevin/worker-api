from celery import Celery
from celery.signals import worker_init

from app.core.config import get_settings

settings = get_settings()


@worker_init.connect
def on_worker_init(**kwargs):
    from app.core.logging import setup_logging
    from app.observability.sentry import init_sentry

    setup_logging(json_output=settings.is_production)
    init_sentry()


def create_celery_app() -> Celery:
    app = Celery(
        "worker-api",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )

    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        # Reliability: acknowledge only after task completes
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        # Worker prefetch: 1 task at a time for fair scheduling
        worker_prefetch_multiplier=1,
        # Result expiry: 24 hours
        result_expires=86400,
        # Auto-discover tasks in these modules
        include=[
            "app.workers.tasks.health_tasks",
            "app.workers.tasks.cleanup_tasks",
            "app.adapters.ebay.tasks",
        ],
    )

    app.conf.beat_schedule = {}

    try:
        from app.workers.scheduling.beat_schedule import BEAT_SCHEDULE

        app.conf.beat_schedule = BEAT_SCHEDULE
    except ImportError:
        pass

    return app


celery_app = create_celery_app()
