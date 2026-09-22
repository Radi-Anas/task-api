from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task_invalid_data():
    response = client.post(
        "/tasks",
        json={
            "title": {"invalid": "value"}
        }
    )

    assert response.status_code == 422


def test_create_task_missing_title():
    response = client.post(
        "/tasks",
        json={
            "completed": False
        }
    )

    assert response.status_code == 422


def test_get_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Integration test task",
            "completed": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Integration test task"
    assert data["completed"] is False
    assert "id" in data


def test_created_task_exists():
    response = client.get("/tasks")

    assert response.status_code == 200

    tasks = response.json()

    assert any(
        task["title"] == "Integration test task"
        for task in tasks
    )