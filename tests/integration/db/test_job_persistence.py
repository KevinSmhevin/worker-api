"""Integration tests for database model persistence.

These tests validate model instantiation and schema structure.
Full persistence tests require a Postgres instance.
"""

import uuid

from app.core.constants import JobStatus, TaskRunStatus
from app.db.models.job import Job
from app.db.models.normalized_record import NormalizedRecord
from app.db.models.raw_artifact import RawArtifact
from app.db.models.task_run import TaskRun


class TestJobModel:
    def test_create_job_instance(self):
        job = Job(
            type="scrape_ebay_sold",
            status=JobStatus.PENDING,
            payload={"url": "https://ebay.com/test"},
        )
        assert job.type == "scrape_ebay_sold"
        assert job.status == JobStatus.PENDING
        assert job.payload["url"] == "https://ebay.com/test"

    def test_job_default_status(self):
        job = Job(type="test")
        assert job.status is None or job.status == JobStatus.PENDING


class TestTaskRunModel:
    def test_create_task_run_instance(self):
        job_id = uuid.uuid4()
        task_run = TaskRun(
            job_id=job_id,
            task_name="scrape_ebay_sold_listings",
            status=TaskRunStatus.RUNNING,
            attempt=1,
        )
        assert task_run.job_id == job_id
        assert task_run.task_name == "scrape_ebay_sold_listings"
        assert task_run.attempt == 1


class TestNormalizedRecordModel:
    def test_create_record_instance(self):
        record = NormalizedRecord(
            card_name="Charizard",
            set_name="Champion's Path",
            card_number="074/073",
            grading_company="PSA",
            grade="10",
            price=450.00,
            source="ebay",
            content_hash="abc123",
        )
        assert record.card_name == "Charizard"
        assert record.grading_company == "PSA"
        assert record.source == "ebay"


class TestRawArtifactModel:
    def test_create_artifact_instance(self):
        artifact = RawArtifact(
            task_run_id=uuid.uuid4(),
            content_hash="def456",
            storage_path="/raw_html/ebay/def456.html",
        )
        assert artifact.content_hash == "def456"
        assert artifact.storage_path.endswith(".html")
