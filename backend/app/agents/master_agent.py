from app.llm.base import LLMProvider


class MasterAgent:
    """Routes user messages to the correct subagent."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def route(self, message: str, chat_history: list[dict] | None = None) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the master agent for a personal assistant. "
                    "Decide whether the user is asking to create a reminder task. "
                    "Only classify as reminder when the user explicitly says something like "
                    "'remind me', 'reminder', or clearly asks to be reminded. "
                    "If the recent assistant message asked a reminder follow-up and the user is "
                    "answering that follow-up, classify it as reminder. "
                    "Return only JSON with keys: intent, agent, confidence, needs_follow_up, "
                    "follow_up_question. intent must be reminder or general. "
                    "agent must be reminder_agent or none."
                ),
            }
        ]
        messages.extend(chat_history or [])
        if not chat_history:
            messages.append({"role": "user", "content": message})

        return await self.llm_provider.chat_json(
            messages
        )
