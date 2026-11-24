import os

import psycopg2
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Entering the context starts the FastAPI lifespan and initializes the pool.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def clean_tasks(client):
    """
    Empty the tasks table before each database integration test.

    Run the test suite only against a dedicated test database. The default
    database name can be overridden with DB_NAME.
    """
    pool = app.state.db_pool
    connection = pool.getconn()

    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE tasks RESTART IDENTITY")
        connection.commit()
    finally:
        pool.putconn(connection)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "version": "3",
    }


def test_create_task_invalid_data(client):
    response = client.post(
        "/tasks",
        json={"title": {"invalid": "value"}},
    )

    assert response.status_code == 422


def test_create_task_missing_title(client):
    response = client.post(
        "/tasks",
        json={"completed": False},
    )

    assert response.status_code == 422


def test_get_tasks(client, clean_tasks):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client, clean_tasks):
    response = client.post(
        "/tasks",
        json={
            "title": "Integration test task",
            "completed": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Integration test task"
    assert data["completed"] is False
    assert isinstance(data["id"], int)


def test_created_task_exists(client, clean_tasks):
    created = client.post(
        "/tasks",
        json={"title": "Persisted task"},
    )
    assert created.status_code == 200

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [created.json()]
