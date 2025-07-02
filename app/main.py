from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

from app.models import Product  # noqa: F401

DATABASE_URL = "sqlite:///gift.db"
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
