"""FastAPI application for ExcuseForge."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os

from app.database import engine, get_db, Base
from app.models import Excuse
from app.excuse_generator import generate_excuse
from app.github_analyzer import get_lab_context

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ExcuseForge", version="1.0.0")


# --- Pydantic schemas ---

class ExcuseResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    lab_number: int | None = None
    upvotes: int = 0
    downvotes: int = 0

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    lab_number: int | None = Field(None, ge=1, le=20)


class VoteRequest(BaseModel):
    direction: str = Field(pattern="^(up|down)$")


# --- API Routes ---

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "ExcuseForge"}


@app.get("/api/labs")
def get_labs():
    """Get lab information analyzed from user's GitHub repositories."""
    return get_lab_context()


@app.post("/api/excuses", response_model=ExcuseResponse)
def generate(request: GenerateRequest | None = None, db: Session = Depends(get_db)):
    """Generate a new excuse and save it to the database."""
    lab_number = request.lab_number if request else None
    text = generate_excuse(lab_number)

    excuse = Excuse(text=text, lab_number=lab_number)
    db.add(excuse)
    db.commit()
    db.refresh(excuse)

    return excuse


@app.get("/api/excuses", response_model=list[ExcuseResponse])
def list_excuses(db: Session = Depends(get_db), limit: int = 50):
    """List recent excuses, optionally filtered by lab."""
    query = db.query(Excuse).order_by(Excuse.created_at.desc())
    return query.limit(limit).all()


@app.get("/api/excuses/{excuse_id}", response_model=ExcuseResponse)
def get_excuse(excuse_id: int, db: Session = Depends(get_db)):
    """Get a specific excuse by ID."""
    excuse = db.query(Excuse).filter(Excuse.id == excuse_id).first()
    if not excuse:
        raise HTTPException(status_code=404, detail="Excuse not found")
    return excuse


@app.post("/api/excuses/{excuse_id}/vote", response_model=ExcuseResponse)
def vote_excuse(excuse_id: int, vote: VoteRequest, db: Session = Depends(get_db)):
    """Vote on an excuse (V2 feature)."""
    excuse = db.query(Excuse).filter(Excuse.id == excuse_id).first()
    if not excuse:
        raise HTTPException(status_code=404, detail="Excuse not found")

    if vote.direction == "up":
        excuse.upvotes += 1
    else:
        excuse.downvotes += 1

    db.commit()
    db.refresh(excuse)
    return excuse


# --- Static files (web client) ---

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    """Serve the main web page."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Static files not found. Run 'npm run build' or check deployment."}
