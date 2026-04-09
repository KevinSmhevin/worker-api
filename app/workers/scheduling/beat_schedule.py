from celery.schedules import crontab

BEAT_SCHEDULE = {
    "health-ping-every-5-minutes": {
        "task": "workers.tasks.health.ping",
        "schedule": crontab(minute="*/5"),
    },
    "cleanup-old-runs-daily": {
        "task": "workers.tasks.cleanup.cleanup_old_runs",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {"older_than_days": 30},
    },
}
