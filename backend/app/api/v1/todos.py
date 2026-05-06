from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def todo_status() -> dict[str, str]:
    return {"status": "todo api ready"}
