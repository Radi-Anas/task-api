import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    title: str
    completed: bool = False


def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        database="taskdb",
        user="taskuser",
        password="taskpassword"
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/tasks")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, completed
        FROM tasks
        ORDER BY id
    """)

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": task[0],
            "title": task[1],
            "completed": task[2]
        }
        for task in tasks
    ]


@app.post("/tasks")
def create_task(task: Task):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, completed)
        VALUES (%s, %s)
        RETURNING id, title, completed
        """,
        (task.title, task.completed)
    )

    new_task = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": new_task[0],
        "title": new_task[1],
        "completed": new_task[2]
    }