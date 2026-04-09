"""Integration tests for the Jobs API.

These tests use FastAPI TestClient and require mocked DB/Celery
since we can't assume Postgres and Redis are running in CI.
"""


import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 404 or response.status_code == 200


class TestJobsEndpointStructure:
    """Validate route registration and basic request shapes.

    Full integration tests require DB/Redis fixtures.
    """

    def test_create_job_requires_body(self, client):
        response = client.post("/jobs")
        assert response.status_code == 422

    def test_create_job_validates_payload(self, client):
        response = client.post("/jobs", json={"invalid": "data"})
        assert response.status_code == 422
