# ==========================
# Rate Limiting
# ==========================
MAX_REQUESTS_PER_MINUTE = 20

# ==========================
# Token Limits
# ==========================
MAX_INPUT_TOKENS = 8000
MAX_OUTPUT_TOKENS = 2048

# ==========================
# Tool Limits
# ==========================
MAX_TOOL_CALLS = 5

# ==========================
# Semantic Cache
# ==========================
CACHE_SIMILARITY_THRESHOLD = 0.85

# ==========================
# Memory
# ==========================
MEMORY_SIMILARITY_THRESHOLD = 0.75

# ==========================
# Web Search
# ==========================
MAX_WEB_RESULTS = 5

# ==========================
# Chat
# ==========================
MAX_CHAT_TITLE_LENGTH = 50
MAX_MESSAGE_LENGTH = 10000

# ==========================
# Feedback
# ==========================
THUMBS_UP = "up"
THUMBS_DOWN = "down"
# ==========================
# Tool Names
# ==========================

TOOL_CALCULATOR = "calculator"
TOOL_WEATHER = "weather"
TOOL_WEB_SEARCH = "web_search"
TOOL_ASK_USER = "ask_user"
TOOL_FETCH_MEMORY = "fetch_from_memory"
TOOL_SAVE_MEMORY = "save_into_memory"

CHROMA_COLLECTION_NAME = "user_memories"

MAX_HISTORY_MESSAGES = 20