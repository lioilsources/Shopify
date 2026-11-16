from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from brain import admin, chat, ingest, public
from brain.search import search_mode
from brain.config import settings

app = FastAPI(title="ChatShop brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm": "connected" if settings.llm_enabled else "mock",
        "embeddings": "connected" if settings.embeddings_enabled else "mock",
        "search": search_mode(),
    }
