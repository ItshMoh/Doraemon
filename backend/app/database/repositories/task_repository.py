from datetime import datetime, timezone

from app.database.client import get_supabase_client


class TaskRepository:
    """Persistence methods for reminder tasks."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    def create_from_extraction(
        self,
        extraction: dict,
        source_chat_message_id: str,
        agent_run_id: str | None = None,
    ) -> dict:
        result = (
            self.client.table("tasks")
            .insert(
                {
                    "source_chat_message_id": source_chat_message_id,
                    "agent_run_id": agent_run_id,
                    "title": extraction["title"],
                    "todo_date": extraction["todo_date"],
                    "reminder_start_date": extraction["reminder_start_date"],
                    "timezone": extraction["timezone"],
                    "metadata": {"target_date": extraction.get("target_date")},
                }
            )
            .execute()
        )
        return result.data[0]

    def get_by_id(self, task_id: str) -> dict | None:
        result = (
            self.client.table("tasks")
            .select("*")
            .eq("id", task_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def list_by_status(self, status: str) -> list[dict]:
        result = (
            self.client.table("tasks")
            .select("*")
            .eq("status", status)
            .order("todo_date", desc=False)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data

    def update_title(self, task_id: str, title: str) -> dict | None:
        result = (
            self.client.table("tasks")
            .update({"title": title.strip()})
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def mark_completed(self, task_id: str) -> dict | None:
        result = (
            self.client.table("tasks")
            .update(
                {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else None
