import { FormEvent, useEffect, useRef, useState } from "react";

import { sendChatMessage } from "../services/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content: "Tell me what to remind you about.",
};

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const windowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (windowRef.current) {
      windowRef.current.scrollTop = windowRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setSending(true);

    try {
      const response = await sendChatMessage(trimmed);
      setMessages((prev) => [...prev, { role: "assistant", content: response.message }]);
    } catch (error) {
      const detail =
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Something went wrong. Try again.";
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${detail}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h2>Chat</h2>
      </header>
      <section className="chat-window" ref={windowRef}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={message.role === "user" ? "user-message" : "assistant-message"}
          >
            {message.content}
          </div>
        ))}
        {sending && <div className="assistant-message assistant-typing">Thinking...</div>}
      </section>
      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          placeholder="Type a reminder..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
