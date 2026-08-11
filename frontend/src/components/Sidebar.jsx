export default function Sidebar({
  chats,
  activeChatId,
  username,
  onNewChat,
  onSelectChat,
  onLogout
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <span className="brand-dot">✦</span>
          <span>AI Assistant</span>
        </div>

        <button className="new-chat-button" onClick={onNewChat}>
          <span>＋</span>
          New chat
        </button>
      </div>

      <div className="chat-list">
        {chats.length === 0 ? (
          <div className="empty-sidebar">No conversations yet.</div>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              className={`chat-list-item ${
                activeChatId === chat.id ? "active" : ""
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <span className="chat-icon">◌</span>
              <span className="chat-title">{chat.title || "New Chat"}</span>
            </button>
          ))
        )}
      </div>

      <div className="sidebar-bottom">
        <div className="user-card">
          <div className="avatar">
            {(username || "U").charAt(0).toUpperCase()}
          </div>
          <div className="user-name">{username || "User"}</div>
        </div>

        <button className="logout-button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
