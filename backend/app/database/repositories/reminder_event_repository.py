from datetime import datetime, timezone

from app.database.client import get_supabase_client


class ReminderEventRepository:
    """Persistence methods for reminder delivery events."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    def get_open_tasks_due(self, today_date: str) -> list[dict]:
        """Return open tasks whose reminder_start_date <= today."""
        result = (
            self.client.table("tasks")
            .select("*")
            .eq("status", "open")
            .lte("reminder_start_date", today_date)
            .order("todo_date", desc=False)
            .execute()
        )
        return result.data

    def was_already_sent(self, task_id: str, scheduled_for: str) -> bool:
        """Check if a reminder was already sent for this task at this time slot."""
        result = (
            self.client.table("reminder_events")
            .select("id")
            .eq("task_id", task_id)
            .eq("scheduled_for", scheduled_for)
            .eq("channel", "telegram")
            .eq("status", "sent")
            .limit(1)
            .execute()
        )
        return len(result.data) > 0

    def log_sent(self, task_id: str, scheduled_for: str, message: str) -> dict:
        """Log a successfully sent reminder."""
        result = (
            self.client.table("reminder_events")
            .insert(
                {
                    "task_id": task_id,
                    "scheduled_for": scheduled_for,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "channel": "telegram",
                    "status": "sent",
                    "message": message,
                }
            )
            .execute()
        )
        return result.data[0]

    def log_failed(self, task_id: str, scheduled_for: str, error: str) -> dict:
        """Log a failed reminder attempt."""
        result = (
            self.client.table("reminder_events")
            .insert(
                {
                    "task_id": task_id,
                    "scheduled_for": scheduled_for,
                    "channel": "telegram",
                    "status": "failed",
                    "error": error,
                }
            )
            .execute()
        )
        return result.data[0]
