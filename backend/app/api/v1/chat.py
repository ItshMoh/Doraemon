import httpx
from fastapi import APIRouter, HTTPException

from app.agents.master_agent import MasterAgent
from app.agents.reminder_agent import ReminderAgent
from app.core.config import settings
from app.database.repositories.agent_run_repository import AgentRunRepository
from app.database.repositories.chat_repository import ChatRepository
from app.database.repositories.task_repository import TaskRepository
from app.llm.openai_provider import get_llm_provider
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()


def current_llm_model() -> str:
    if settings.llm_provider == "openrouter" and settings.openrouter_model:
        return settings.openrouter_model
    return settings.openai_model


@router.get("/")
def chat_status() -> dict[str, str]:
    return {"status": "chat api ready"}


@router.post("/", response_model=ChatResponse)
async def create_chat_message(payload: ChatRequest) -> ChatResponse:
    chat_repository = ChatRepository()
    task_repository = TaskRepository()
    agent_run_repository = AgentRunRepository()
    llm_provider = get_llm_provider()

    user_message = chat_repository.create("user", payload.message)
    chat_history = chat_repository.list_recent()
    master_agent = MasterAgent(llm_provider)
    reminder_agent = ReminderAgent(llm_provider)

    try:
        route = await master_agent.route(payload.message, chat_history)
        route_status = "needs_follow_up" if route.get("needs_follow_up") else "success"
        agent_run_repository.create(
            chat_message_id=user_message["id"],
            agent_name="master_agent",
            llm_provider=settings.llm_provider,
            llm_model=current_llm_model(),
            status=route_status,
            input_data={"message": payload.message},
            output_data=route,
        )

        if route.get("needs_follow_up"):
            reply = route.get("follow_up_question") or "What should I remind you about?"
            chat_repository.create("assistant", reply, {"route": route})
            return ChatResponse(message=reply, needs_follow_up=True)

        if route.get("intent") != "reminder" or route.get("agent") != "reminder_agent":
            reply = "I saved your message. Tell me with 'remind me' when you want a todo created."
            chat_repository.create("assistant", reply, {"route": route})
            return ChatResponse(message=reply)

        extraction = await reminder_agent.extract_task(payload.message, chat_history)
        extraction_status = (
            "needs_follow_up" if extraction.get("needs_follow_up") else "success"
        )
        extraction_run = agent_run_repository.create(
            chat_message_id=user_message["id"],
            agent_name="reminder_agent",
            llm_provider=settings.llm_provider,
            llm_model=current_llm_model(),
            status=extraction_status,
            input_data={"message": payload.message},
            output_data=extraction,
        )

        if extraction.get("needs_follow_up") or not extraction.get("has_reminder"):
            reply = extraction.get("follow_up_question") or "What should I remind you about?"
            chat_repository.create("assistant", reply, {"extraction": extraction})
            return ChatResponse(message=reply, needs_follow_up=True)

        task = task_repository.create_from_extraction(
            extraction=extraction,
            source_chat_message_id=user_message["id"],
            agent_run_id=extraction_run["id"],
        )
        reply = (
            f"Reminder created: {task['title']}. "
            f"Todo date: {task['todo_date']}."
        )
        chat_repository.create("assistant", reply, {"task_id": task["id"]})
        return ChatResponse(message=reply, task_created=True, task=task)

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider request failed: {exc.response.text}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
