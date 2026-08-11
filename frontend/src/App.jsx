import { useEffect, useState } from "react";
import { api } from "./services/api";
import Login from "./components/Login";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";

function historyToUi(history) {
  return (history || []).map((item, index) => ({
    id: item.id ?? item.message_id ?? null,
    role: item.role,
    content: item.content || "",
    model: item.model ?? null,
    index
  }));
}

export default function App() {
  const [auth, setAuth] = useState(() => {
    const token = localStorage.getItem("access_token");
    const user = localStorage.getItem("user");
    return token && user
      ? { token, user: JSON.parse(user) }
      : null;
  });

  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadChats(preferredId = null) {
    const result = await api.getChats();
    const list = Array.isArray(result) ? result : [];

    setChats(list);

    const target =
      preferredId ??
      activeChatId ??
      list[0]?.id ??
      null;

    if (target) {
      await openChat(target, list);
    } else {
      setActiveChatId(null);
      setActiveChat(null);
      setMessages([]);
    }
  }

  async function openChat(chatId, knownChats = chats) {
    setError("");

    const history = await api.getChatHistory(chatId);
    const chat =
      knownChats.find((item) => item.id === chatId) ||
      chats.find((item) => item.id === chatId) ||
      { id: chatId, title: "Chat" };

    setActiveChatId(chatId);
    setActiveChat(chat);
    setMessages(historyToUi(history));
  }

  useEffect(() => {
    if (!auth) return;

    loadChats().catch((err) => {
      if (err.message.toLowerCase().includes("401")) {
        logout();
      } else {
        setError(err.message);
      }
    });
  }, [auth]);

  async function login(email, password) {
    const result = await api.login(email, password);

    if (result.success) {
      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("user", JSON.stringify(result.user));
      setAuth({
        token: result.access_token,
        user: result.user
      });
    }

    return result;
  }

  async function register(username, email, password) {
    return api.register(username, email, password);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setAuth(null);
    setChats([]);
    setActiveChatId(null);
    setActiveChat(null);
    setMessages([]);
  }

  async function newChat() {
    try {
      setError("");
      const chat = await api.createChat();
      await loadChats(chat.id);
    } catch (err) {
      setError(err.message);
    }
  }

  async function sendMessage(text) {
    if (!activeChatId) return;

    setError("");

    const optimistic = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: text
    };

    setMessages((current) => [...current, optimistic]);
    setLoading(true);

    try {
      const result = await api.sendMessage(activeChatId, text);

      // The current backend returns the response but not the
      // assistant message id. Reloading history keeps the UI
      // synchronized with SQLite and gives feedback a real id.
      const history = await api.getChatHistory(activeChatId);
      setMessages(historyToUi(history));

      if (result?.awaiting_user) {
        // The next normal message continues the conversation.
        // The backend currently needs an interrupt-resume endpoint
        // for true ask_user pause/resume behavior.
      }
    } catch (err) {
      setMessages((current) =>
        current.filter((message) => message.id !== optimistic.id)
      );
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(message, feedbackType) {
    if (!message.id) {
      setError(
        "This response has no message id yet. Reload the chat and try again."
      );
      return;
    }

    try {
      await api.submitFeedback(message.id, feedbackType);

      setMessages((current) =>
        current.map((item) =>
          item.id === message.id
            ? { ...item, feedback: feedbackType }
            : item
        )
      );
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRetry(message) {
    if (!message.id) return;

    try {
      const previousUserMessage = [...messages]
        .slice(0, messages.indexOf(message))
        .reverse()
        .find((item) => item.role === "user");

      if (!previousUserMessage) {
        throw new Error("Could not find the original user message.");
      }

      const result = await api.retry(
        previousUserMessage.content,
        message.model,
        null
      );

      if (result?.response) {
        setMessages((current) =>
          current.map((item) =>
            item.id === message.id
              ? {
                  ...item,
                  content: result.response,
                  model: result.model,
                  feedback: null
                }
              : item
          )
        );
      }
    } catch (err) {
      setError(err.message);
    }
  }

  if (!auth) {
    return <Login onLogin={login} onRegister={register} />;
  }

  return (
    <div className="app-shell">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        username={auth.user?.username}
        onNewChat={newChat}
        onSelectChat={(id) => openChat(id)}
        onLogout={logout}
      />

      <div className="main-area">
        {error && (
          <div className="global-error">
            <span>{error}</span>
            <button onClick={() => setError("")}>×</button>
          </div>
        )}

        <ChatWindow
          chat={activeChat}
          messages={messages}
          loading={loading}
          onSend={sendMessage}
          onFeedback={handleFeedback}
          onRetry={handleRetry}
        />
      </div>
    </div>
  );
}
