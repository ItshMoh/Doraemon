from fastapi import APIRouter, HTTPException

from app.database.repositories.task_repository import TaskRepository
from app.schemas.todos import TaskGroupResponse, TaskResponse, TaskUpdateRequest


router = APIRouter()


@router.get("/")
def todo_status() -> dict[str, str]:
    return {"status": "todo api ready"}


def group_tasks_by_todo_date(tasks: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}

    for task in tasks:
        grouped.setdefault(task["todo_date"], []).append(task)

    return {
        "groups": [
            {"date": todo_date, "tasks": grouped[todo_date]}
            for todo_date in sorted(grouped)
        ]
    }


@router.get("/open", response_model=TaskGroupResponse)
def list_open_todos() -> dict:
    tasks = TaskRepository().list_by_status("open")
    return group_tasks_by_todo_date(tasks)


@router.get("/history", response_model=TaskGroupResponse)
def list_completed_todos() -> dict:
    tasks = TaskRepository().list_by_status("completed")
    return group_tasks_by_todo_date(tasks)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> dict:
    task = TaskRepository().get_by_id(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_title(task_id: str, payload: TaskUpdateRequest) -> dict:
    title = payload.title.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Task title cannot be empty.")

    task = TaskRepository().update_title(task_id, title)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str) -> dict:
    repository = TaskRepository()
    existing_task = repository.get_by_id(task_id)

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if existing_task["status"] == "completed":
        return existing_task

    task = repository.mark_completed(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task
