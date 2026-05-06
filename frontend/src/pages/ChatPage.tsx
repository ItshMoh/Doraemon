export function ChatPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h2>Chat</h2>
      </header>
      <section className="chat-window">
        <div className="assistant-message">Tell me what to remind you about.</div>
      </section>
      <form className="chat-form">
        <input placeholder="Type a reminder..." />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
