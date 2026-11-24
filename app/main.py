from contextlib import asynccontextmanager
import os
from typing import Generator

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from psycopg2.extensions import connection as PostgreSQLConnection
from psycopg2.pool import ThreadedConnectionPool


def create_connection_pool() -> ThreadedConnectionPool:
    """Create a bounded, thread-safe pool for PostgreSQL connections."""
    return ThreadedConnectionPool(
        minconn=int(os.getenv("DB_POOL_MIN", "1")),
        maxconn=int(os.getenv("DB_POOL_MAX", "10")),
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "taskdb"),
        user=os.getenv("DB_USER", "taskuser"),
        password=os.getenv("DB_PASSWORD", "taskpassword"),
    )


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db_pool = create_connection_pool()
    try:
        yield
    finally:
        application.state.db_pool.closeall()


app = FastAPI(
    title="Task API",
    description="A task management API built with FastAPI and PostgreSQL.",
    version="3.0.0",
    lifespan=lifespan,
)


class Task(BaseModel):
    title: str
    completed: bool = False


def get_db() -> Generator[PostgreSQLConnection, None, None]:
    """Borrow a connection for one request and always return it to the pool."""
    pool: ThreadedConnectionPool = app.state.db_pool
    connection = pool.getconn()

    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        pool.putconn(connection)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "3"}


@app.get("/tasks")
def get_tasks(connection: PostgreSQLConnection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, completed
            FROM tasks
            ORDER BY id
            """
        )
        tasks = cursor.fetchall()

    return [
        {"id": task[0], "title": task[1], "completed": task[2]}
        for task in tasks
    ]


@app.post("/tasks")
def create_task(
    task: Task,
    connection: PostgreSQLConnection = Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO tasks (title, completed)
            VALUES (%s, %s)
            RETURNING id, title, completed
            """,
            (task.title, task.completed),
        )
        new_task = cursor.fetchone()

    connection.commit()

    return {
        "id": new_task[0],
        "title": new_task[1],
        "completed": new_task[2],
    }
