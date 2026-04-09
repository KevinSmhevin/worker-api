from app.celery_app import celery_app


@celery_app.task(name="workers.tasks.health.ping", bind=True)
def ping(self):
    """Simple health check task to verify Celery is working."""
    return {"status": "pong", "task_id": self.request.id}
