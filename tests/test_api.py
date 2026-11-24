import uuid

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
def task_title():
    """Generate a unique title and remove only this test's record afterwards."""
    title = f"pytest-task-{uuid.uuid4()}"

    yield title

    pool = app.state.db_pool
    connection = pool.getconn()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE title = %s", (title,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
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


def test_get_tasks(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task(client, task_title):
    response = client.post(
        "/tasks",
        json={
            "title": task_title,
            "completed": False,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == task_title
    assert data["completed"] is False
    assert isinstance(data["id"], int)


def test_created_task_exists(client, task_title):
    created = client.post(
        "/tasks",
        json={"title": task_title},
    )
    assert created.status_code == 200

    response = client.get("/tasks")

    assert response.status_code == 200
    assert created.json() in response.json()
