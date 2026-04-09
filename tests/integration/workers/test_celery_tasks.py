"""Integration tests for Celery tasks.

These tests validate task registration and basic structure.
Full integration requires Redis broker running.
"""

import importlib

import pytest

from app.celery_app import celery_app


@pytest.fixture(autouse=True)
def _load_task_modules():
    """Force-load task modules so decorators register with Celery."""
    importlib.import_module("app.workers.tasks.health_tasks")
    importlib.import_module("app.workers.tasks.cleanup_tasks")
    importlib.import_module("app.adapters.ebay.tasks")


class TestCeleryTaskRegistration:
    def test_health_ping_registered(self):
        assert "workers.tasks.health.ping" in celery_app.tasks

    def test_cleanup_registered(self):
        assert "workers.tasks.cleanup.cleanup_old_runs" in celery_app.tasks

    def test_ebay_scrape_registered(self):
        assert "adapters.ebay.scrape_sold_listings" in celery_app.tasks
