import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({
  chat,
  messages,
  loading,
  onSend,
  onFeedback,
  onRetry
}) {
  const [input, setInput] = useState("");
  const [retryingId, setRetryingId] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function submit(e) {
    e.preventDefault();

    const text = input.trim();
    if (!text || loading || !chat) return;

    setInput("");
    await onSend(text);
  }

  async function retry(message) {
    setRetryingId(message.id);

    try {
      await onRetry(message);
    } finally {
      setRetryingId(null);
    }
  }

  if (!chat) {
    return (
      <main className="chat-empty">
        <div className="welcome-icon">✦</div>
        <h2>How can I help you today?</h2>
        <p>Ask a question, solve a problem, or start a conversation.</p>
      </main>
    );
  }

  return (
    <main className="chat-window">
      <header className="chat-header">
        <div>
          <h2>{chat.title || "New Chat"}</h2>
          <span>AI Assistant</span>
        </div>
      </header>

      <section className="messages">
        {messages.length === 0 ? (
          <div className="chat-start">
            <div className="welcome-icon">✦</div>
            <h2>How can I help?</h2>
            <p>Your conversation will appear here.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble
              key={message.id ?? `${message.role}-${index}`}
              message={message}
              onFeedback={onFeedback}
              onRetry={retry}
              retrying={retryingId === message.id}
            />
          ))
        )}

        {loading && (
          <div className="message-row assistant-row">
            <div className="assistant-avatar">✦</div>
            <div className="typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </section>

      <form className="composer" onSubmit={submit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message AI Assistant..."
          rows={1}
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(e);
            }
          }}
        />
        <button
          className="send-button"
          disabled={!input.trim() || loading}
          aria-label="Send"
        >
          ↑
        </button>
      </form>

      <div className="composer-note">
        AI can make mistakes. Check important information.
      </div>
    </main>
  );
}
