from fastapi import APIRouter

from app.api.v1 import chat, todos


router = APIRouter()
router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
router.include_router(todos.router, prefix="/v1/todos", tags=["todos"])
