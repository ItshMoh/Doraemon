class TelegramService:
    """Sends outbound reminder messages through Telegram."""

    async def send_message(self, text: str) -> None:
        raise NotImplementedError("Telegram delivery will be implemented in Phase 5.")
