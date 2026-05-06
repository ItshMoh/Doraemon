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
