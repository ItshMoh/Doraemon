from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.llm.base import LLMProvider


class ReminderAgent:
    """Extracts reminder tasks from user messages."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def extract_task(
        self,
        message: str,
        chat_history: list[dict] | None = None,
    ) -> dict:
        today = datetime.now(ZoneInfo(settings.app_timezone)).date()
        messages = [
            {
                "role": "system",
                "content": (
                    "Extract a reminder task from the conversation. "
                    f"Today's date is {today.isoformat()} in {settings.app_timezone}. "
                    "Return only JSON with keys: has_reminder, needs_follow_up, "
                    "follow_up_question, title, target_date. "
                    "has_reminder is true when the user explicitly asks for a reminder, "
                    "or when the user is answering a recent assistant follow-up about a reminder. "
                    "title must be a concise todo title without 'remind me'. "
                    "target_date must be YYYY-MM-DD when the user gives a date or relative date, "
                    "otherwise null. If the reminder intent exists but the actual task is unclear, "
                    "set needs_follow_up true and write a short follow_up_question."
                ),
            }
        ]
        messages.extend(chat_history or [])
        if not chat_history:
            messages.append({"role": "user", "content": message})

        extracted = await self.llm_provider.chat_json(messages)

        if extracted.get("needs_follow_up") or not extracted.get("has_reminder"):
            return extracted

        target_date = extracted.get("target_date")
        todo_date = today
        reminder_start_date = today

        if target_date:
            todo_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            reminder_start_date = max(today, todo_date - timedelta(days=1))

        extracted["todo_date"] = todo_date.isoformat()
        extracted["reminder_start_date"] = reminder_start_date.isoformat()
        extracted["timezone"] = settings.app_timezone
        return extracted
