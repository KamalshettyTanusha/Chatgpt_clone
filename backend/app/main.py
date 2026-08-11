from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import models so SQLAlchemy can detect them
from app.database import models
from app.database.database import Base, engine
#from app.database.database import engine

# API Routers
from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.feedback_routes import router as feedback_router
from app.api.history_routes import router as history_router
#from app.api.memory_routes import router as memory_router


app = FastAPI(
    title="AI Chat Assistant",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    """
    Create database tables if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # React (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API Routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(feedback_router)
#app.include_router(memory_router)


@app.get("/")
def home():
    """
    Health Check Endpoint
    """
    return {
        "status": "running",
        "application": "AI Chat Assistant Backend",
        "version": "1.0.0"
    }