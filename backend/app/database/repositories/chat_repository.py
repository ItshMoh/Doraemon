from app.database.client import get_supabase_client


class ChatRepository:
    """Persistence methods for chat messages."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    def create(self, role: str, content: str, metadata: dict | None = None) -> dict:
        result = (
            self.client.table("chat_messages")
            .insert(
                {
                    "role": role,
                    "content": content,
                    "metadata": metadata or {},
                }
            )
            .execute()
        )
        return result.data[0]

    def list_recent(self, limit: int = 12) -> list[dict]:
        result = (
            self.client.table("chat_messages")
            .select("role, content, created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        messages = list(reversed(result.data))
        return [
            {"role": message["role"], "content": message["content"]}
            for message in messages
            if message["role"] in {"user", "assistant", "system"}
        ]
