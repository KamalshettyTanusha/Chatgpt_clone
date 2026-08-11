import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({
  message,
  onFeedback,
  onRetry,
  retrying
}) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="message-row user-row">
        <div className="user-bubble">{message.content}</div>
      </div>
    );
  }

  return (
    <div className="message-row assistant-row">
      <div className="assistant-avatar">✦</div>

      <div className="assistant-column">
        <div className="assistant-bubble markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content || ""}
          </ReactMarkdown>
        </div>

        <div className="message-actions">
          <button
            title="Good response"
            className={message.feedback === "positive" ? "selected" : ""}
            onClick={() => onFeedback(message, "positive")}
            disabled={!message.id}
          >
            👍
          </button>

          <button
            title="Bad response"
            className={message.feedback === "negative" ? "selected" : ""}
            onClick={() => onFeedback(message, "negative")}
            disabled={!message.id}
          >
            👎
          </button>

          <button
            title="Retry"
            onClick={() => onRetry(message)}
            disabled={retrying}
          >
            {retrying ? "↻" : "↻"}
          </button>

          {message.model && (
            <span className="model-label">{message.model}</span>
          )}
        </div>
      </div>
    </div>
  );
}
