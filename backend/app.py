from src.modules.agent.rag.ingestion import ingest
from src.modules.auth.router import router as auth_router
from src.modules.ticket.router import router as ticket_router
from src.database.sqlite_config import Base, engine
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os

from dotenv import load_dotenv
load_dotenv()  # load .env before any other imports read os.environ


import src.modules.ticket.model  # noqa: F401
import src.modules.auth.model  # noqa: F401 — register User with Base

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Sync knowledge base into vector store on every startup
ingest()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", os.path.join(
    os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="TonhãoDesk",
    description="API para o TonhãoDesk, um sistema de gerenciamento de chamados.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.include_router(auth_router)
app.include_router(ticket_router)
