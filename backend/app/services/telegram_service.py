import httpx

from app.core.config import settings


class TelegramService:
    """Sends outbound reminder messages through Telegram."""

    def __init__(self) -> None:
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = "https://api.telegram.org"

    async def send_message(self, text: str) -> dict:
        if not self.bot_token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN.")

        if not self.chat_id:
            raise ValueError("Missing TELEGRAM_CHAT_ID.")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "disable_web_page_preview": True,
                },
            )
            response.raise_for_status()
            return response.json()

    async def send_task_reminder(self, task: dict) -> dict:
        return await self.send_message(self.build_task_reminder_message(task))

    def build_task_reminder_message(self, task: dict) -> str:
        return (
            f"Reminder: {task['title']}\n"
            f"Todo date: {task['todo_date']}\n"
            f"Created on: {task['created_at'][:10]}"
        )
