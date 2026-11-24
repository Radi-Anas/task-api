# Task API

A containerized task-management REST API built with **FastAPI** and **PostgreSQL**. The project demonstrates how to package a Python API and its database with Docker Compose, persist database data with a named volume, and verify API behavior with automated tests.

## Features

- **FastAPI REST API** for creating and retrieving tasks.
- **PostgreSQL 15** database with a simple relational schema.
- **Docker** image for the API and **Docker Compose** orchestration for the API and database.
- **Persistent database storage** through the `postgres_data` named volume.
- **Automated API tests** using pytest and FastAPI's `TestClient`.
- **Health endpoint** for a basic service availability check.

## Architecture

```text
Client
  |
  | HTTP :8000
  v
FastAPI application
  |
  | psycopg2 / PostgreSQL :5432
  v
PostgreSQL 15
  |
  v
postgres_data volume
```

Docker Compose starts two services:

| Service | Responsibility | Port |
|---|---|---|
| `api` | Runs the FastAPI application with Uvicorn | `8000` |
| `postgres` | Stores task records in PostgreSQL | `5432` |

The database schema is initialized from `db/init.sql` when PostgreSQL creates a new data directory.

## Tech stack

- Python 3.13
- FastAPI
- Uvicorn
- PostgreSQL 15
- psycopg2
- Docker and Docker Compose
- pytest and HTTPX (FastAPI test client dependency)

## Getting started

### Prerequisites

Install:

- Docker Desktop (or Docker Engine)
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Radi-Anas/task-api.git
cd task-api
```

### 2. Start the application

```bash
docker compose up --build
```

The API will be available at:

- API base URL: http://localhost:8000
- Interactive Swagger documentation: http://localhost:8000/docs
- Alternative ReDoc documentation: http://localhost:8000/redoc

The PostgreSQL service is exposed on port `5432` for local development.

### 3. Stop the application

```bash
docker compose down
```

To remove the database volume as well (this permanently deletes the persisted task data):

```bash
docker compose down -v
```

## API endpoints

### Health check

`GET /health`

Returns the application's basic health status.

Example response:

```json
{
  "status": "healthy",
  "version": "2"
}
```

### Retrieve all tasks

`GET /tasks`

Returns all tasks ordered by their database ID.

Example response:

```json
[
  {
    "id": 1,
    "title": "Learn Docker Compose",
    "completed": false
  }
]
```

### Create a task

`POST /tasks`

Request body:

```json
{
  "title": "Build a FastAPI project",
  "completed": false
}
```

The `title` field is required. The `completed` field is optional and defaults to `false`.

Example response:

```json
{
  "id": 2,
  "title": "Build a FastAPI project",
  "completed": false
}
```

## Database schema

The `tasks` table is defined in `db/init.sql`:

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Auto-generated task identifier |
| `title` | TEXT NOT NULL | Task title |
| `completed` | BOOLEAN | Completion status; defaults to `false` |

## Running tests

The test suite is located in `tests/test_api.py`. It covers:

- Health endpoint response.
- Request validation for invalid or missing task titles.
- Retrieving tasks.
- Creating a task and checking that it appears in the task list.

Run the tests in an environment where the API's Python dependencies are installed and a reachable PostgreSQL database is available:

```bash
pytest -v
```

## Configuration

The API reads its PostgreSQL connection settings from environment variables:

| Variable | Default value |
|---|---|
| `DB_HOST` | `postgres` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `taskdb` |
| `DB_USER` | `taskuser` |
| `DB_PASSWORD` | `taskpassword` |

These values are currently defined directly in `docker-compose.yml` for local development. Replace the example credentials and move secrets to an environment file or secret manager before using the project beyond a local learning environment.

## Project structure

```text
task-api/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI routes and PostgreSQL access
├── db/
│   └── init.sql             # Database initialization script
├── tests/
│   └── test_api.py          # API tests
├── Dockerfile               # API container image
├── docker-compose.yml       # API and PostgreSQL services
├── requirements.txt         # Python dependencies
└── .gitignore
```

## Current scope and possible improvements

The current implementation supports creating and listing tasks. Useful next steps would be:

- Add endpoints to retrieve, update, and delete an individual task.
- Add database connection pooling and safer connection cleanup.
- Add readiness checks and service startup coordination for PostgreSQL.
- Use a `.env` file or a secrets manager instead of hard-coded development credentials.
- Add integration-test database isolation and test fixtures.
- Add CI to run tests automatically on each push or pull request.

---

Built as a hands-on project for learning Python API development, relational database integration, containerization, and service orchestration.
