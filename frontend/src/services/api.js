const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

export const api = {
  async login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  async register(username, email, password) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password })
    });
  },

  async getChats() {
    return request("/history/chats");
  },

  async createChat() {
    return request("/history/new-chat", {
      method: "POST"
    });
  },

  async getChatHistory(chatId) {
    return request(`/history/${chatId}`);
  },

  async sendMessage(chatId, message) {
    return request("/chat/", {
      method: "POST",
      body: JSON.stringify({
        chat_id: chatId,
        message
      })
    });
  },

  async submitFeedback(messageId, feedbackType, comment = null) {
    return request("/feedback/", {
      method: "POST",
      body: JSON.stringify({
        message_id: messageId,
        feedback_type: feedbackType,
        comment
      })
    });
  },

  async retry(query, previousModel, memory = null) {
    return request("/feedback/retry", {
      method: "POST",
      body: JSON.stringify({
        query,
        previous_model: previousModel,
        memory
      })
    });
  }
};
