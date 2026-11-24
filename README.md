# Task API

A containerized task-management REST API built with **FastAPI**, **PostgreSQL 15**, and **Docker Compose**. This project demonstrates API development, database integration, connection pooling, container orchestration, and integration testing.

## Features

- REST endpoints for creating and listing tasks.
- PostgreSQL persistence with a Docker named volume.
- Thread-safe PostgreSQL connection pooling with configurable limits.
- FastAPI dependency injection for request-scoped database connections.
- Pool startup and shutdown managed by the FastAPI application lifespan.
- PostgreSQL health checks and service startup coordination.
- Integration tests using pytest and FastAPI's TestClient.

## Architecture

```text
Client
  | HTTP :8000
  v
FastAPI + Uvicorn
  | psycopg2 connection pool
  v
PostgreSQL 15 :5432
  |
  v
postgres_data volume
```

| Service | Responsibility | Port |
|---|---|---|
| `api` | FastAPI application | `8000` |
| `postgres` | Persistent relational database | `5432` |

The schema is initialized from `db/init.sql` when PostgreSQL initializes a new data directory.

## Tech stack

- Python 3.13
- FastAPI and Uvicorn
- PostgreSQL 15 and psycopg2
- Docker and Docker Compose
- pytest and HTTPX

## Getting started

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Radi-Anas/task-api.git
cd task-api
```

### 2. Configure the database password

Copy the example environment file:

```bash
cp .env.example .env
```

Change `DB_PASSWORD` in `.env` before using the application beyond local experimentation. Docker Compose reads this file automatically.

### 3. Build and start the services

```bash
docker compose up --build -d
```

Check service status and logs:

```bash
docker compose ps
docker compose logs -f api
```

The API is available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Stop the services

```bash
docker compose down
```

To also delete the PostgreSQL volume and all persisted task data:

```bash
docker compose down -v
```

## API endpoints

### Health check

`GET /health`

Example response:

```json
{
  "status": "healthy",
  "version": "3"
}
```

### List tasks

`GET /tasks`

Returns tasks ordered by ID.

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

Request:

```json
{
  "title": "Build a FastAPI project",
  "completed": false
}
```

The `title` field is required. `completed` defaults to `false`.

Example response:

```json
{
  "id": 2,
  "title": "Build a FastAPI project",
  "completed": false
}
```

## Database schema

The `tasks` table is created by `db/init.sql`.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Auto-generated task identifier |
| `title` | TEXT NOT NULL | Task title |
| `completed` | BOOLEAN | Completion status; defaults to `false` |

## Database connection management

The application creates a `ThreadedConnectionPool` during FastAPI startup and closes it during shutdown.

- Each request borrows a connection through the `get_db` dependency.
- The dependency returns the connection to the pool after the request.
- Failed requests roll back their transaction before the connection is reused.
- Pool size is controlled by `DB_POOL_MIN` and `DB_POOL_MAX`.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DB_HOST` | `postgres` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `taskdb` | Database name |
| `DB_USER` | `taskuser` | Database user |
| `DB_PASSWORD` | `taskpassword` | Local development password |
| `DB_POOL_MIN` | `1` | Minimum pooled connections |
| `DB_POOL_MAX` | `10` | Maximum pooled connections |

Do not commit real credentials. The `.env` file is excluded through `.gitignore`.

## Running tests

Start the services first so the API container can connect to PostgreSQL:

```bash
docker compose up --build -d
docker compose exec api pytest -v
```

The tests cover health checks, request validation, task creation, and task retrieval. Each database test uses a unique task title and deletes only its own test record during cleanup; it does not truncate the task table.

The test suite uses the database configured by the container. Do not point it at a production database.

## Project structure

```text
task-api/
├── app/
│   ├── __init__.py
│   └── main.py              # API routes, pool and DB dependency
├── db/
│   └── init.sql             # Database schema
├── tests/
│   └── test_api.py          # API integration tests
├── .env.example             # Example local configuration
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Next improvements

- Add get-by-ID, update, and delete endpoints.
- Add database readiness to the API health check.
- Add migrations with Alembic instead of relying only on initialization SQL.
- Add CI to run tests on every push and pull request.
- Add structured logging and API error handling.

---

Built as a hands-on project for learning backend development, database integration, and containerized services.
