from fastapi import APIRouter

from app.api.v1 import chat, notifications, todos


router = APIRouter()
router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
router.include_router(
    notifications.router,
    prefix="/v1/notifications",
    tags=["notifications"],
)
router.include_router(todos.router, prefix="/v1/todos", tags=["todos"])
