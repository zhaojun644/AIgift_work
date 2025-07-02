from fastapi import FastAPI, Response
from sqlmodel import SQLModel, create_engine
from pydantic import BaseModel
from reportlab.pdfgen import canvas
import io

from app.models import Product  # noqa: F401
from app.recommendation import vector_search

DATABASE_URL = "sqlite:///gift.db"
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI()


class RecommendationRequest(BaseModel):
    text: str
    budget: float

@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/recommend")
def recommend(req: RecommendationRequest) -> list[dict]:
    """Return top 5 recommended products within the budget."""
    return vector_search(req.text, req.budget, limit=5)


@app.post("/plan")
def plan(req: RecommendationRequest) -> Response:
    """Generate a PDF plan of recommended products."""
    products = vector_search(req.text, req.budget, limit=5)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, "Gift Plan")
    y -= 30
    for p in products:
        line = f"{p.get('name', '')} - ${p.get('price', 0)}"
        pdf.drawString(50, y, line)
        y -= 20
    pdf.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    headers = {"Content-Disposition": "attachment; filename=plan.pdf"}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
