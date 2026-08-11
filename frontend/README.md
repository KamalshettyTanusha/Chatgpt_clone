# AI Chat Assistant Frontend

React + Vite frontend for the existing FastAPI/LangGraph backend.

## Run

1. Copy `.env.example` to `.env`.
2. Set `VITE_API_BASE_URL=http://localhost:8000`.
3. Run `npm install`.
4. Run `npm run dev`.

The backend CORS configuration already allows `http://localhost:5173`.

## Backend endpoints used

- POST `/auth/login`
- POST `/auth/register`
- GET `/history/chats`
- POST `/history/new-chat`
- GET `/history/{chat_id}`
- POST `/chat/`
- POST `/feedback/`
- POST `/feedback/retry`

## Important current-backend limitation

The current `/chat/` response does not return the assistant message id.
After sending a message, the frontend therefore reloads `/history/{chat_id}` so
the saved SQLite message id is available for feedback.

The current retry endpoint regenerates a response but does not persist the retry
as a new assistant message. The UI replaces the displayed response locally.

The current `ask_user` LangGraph tool uses `interrupt()`. A true ChatGPT-style
pause -> user answer -> graph resume flow requires the backend to resume the
same LangGraph thread with `Command(resume=...)`; the current `chat_service.py`
uses a plain `agent_graph.invoke()` and does not expose that resume operation.
