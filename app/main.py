"""FastAPI application for ExcuseForge."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os

from app.database import engine, get_db, Base
from app.models import Excuse, SavedRepo, Vote
from app.excuse_generator import generate_excuse
from app.github_analyzer import get_lab_context
from starlette.requests import Request

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
    repo_id: int | None = None
    user_vote: str | None = None  # "up", "down", or None

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    lab_number: int | None = Field(None, ge=1, le=20)
    repo_id: int | None = None  # Generate excuse based on saved repo


class VoteRequest(BaseModel):
    direction: str = Field(pattern="^(up|down)$")


class SavedRepoResponse(BaseModel):
    id: int
    github_url: str
    repo_name: str
    description: str | None = None
    lab_number: int | None = None
    technologies: list[str] | None = None
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(repo):
        import json
        techs = None
        if repo.technologies:
            try:
                techs = json.loads(repo.technologies)
            except json.JSONDecodeError:
                techs = None
        return {
            "id": repo.id,
            "github_url": repo.github_url,
            "repo_name": repo.repo_name,
            "description": repo.description,
            "lab_number": repo.lab_number,
            "technologies": techs,
            "created_at": repo.created_at,
        }


class AddRepoRequest(BaseModel):
    github_url: str
    lab_number: int | None = Field(None, ge=1, le=20)


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
    repo_id = request.repo_id if request else None

    # If repo_id provided, use the saved repo's lab number and tech context
    if repo_id:
        repo = db.query(SavedRepo).filter(SavedRepo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Saved repo not found")
        # Override with the repo's lab number if available
        lab_number = repo.lab_number or lab_number
        text = generate_excuse(lab_number)
    else:
        text = generate_excuse(lab_number)

    excuse = Excuse(text=text, lab_number=lab_number, repo_id=repo_id)
    db.add(excuse)
    db.commit()
    db.refresh(excuse)

    return excuse


@app.get("/api/excuses", response_model=list[dict])
def list_excuses(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 50,
    lab_number: int | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    q: str | None = None,
):
    """List excuses with optional filtering, sorting, and full-text search."""
    valid_sort = {"created_at", "upvotes", "downvotes"}
    valid_order = {"asc", "desc"}
    if sort_by not in valid_sort:
        sort_by = "created_at"
    if order not in valid_order:
        order = "desc"

    query = db.query(Excuse)

    # Filter by lab
    if lab_number is not None:
        query = query.filter(Excuse.lab_number == lab_number)

    # Full-text search on excuse text
    if q:
        query = query.filter(Excuse.text.ilike(f"%{q}%"))

    # Apply sorting
    sort_col = getattr(Excuse, sort_by)
    if order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    excuses = query.limit(limit).all()

    # Build vote lookup for this user
    client_ip = request.client.host
    excuse_ids = [e.id for e in excuses]
    votes = db.query(Vote).filter(
        Vote.excuse_id.in_(excuse_ids),
        Vote.voter_ip == client_ip,
    ).all() if excuse_ids else []
    vote_map = {v.excuse_id: v.direction for v in votes}

    return [
        {
            "id": e.id,
            "text": e.text,
            "created_at": e.created_at,
            "lab_number": e.lab_number,
            "upvotes": e.upvotes,
            "downvotes": e.downvotes,
            "repo_id": e.repo_id,
            "user_vote": vote_map.get(e.id),
        }
        for e in excuses
    ]


@app.get("/api/excuses/{excuse_id}", response_model=dict)
def get_excuse(excuse_id: int, request: Request, db: Session = Depends(get_db)):
    """Get a specific excuse by ID."""
    excuse = db.query(Excuse).filter(Excuse.id == excuse_id).first()
    if not excuse:
        raise HTTPException(status_code=404, detail="Excuse not found")

    client_ip = request.client.host
    vote = db.query(Vote).filter(
        Vote.excuse_id == excuse_id,
        Vote.voter_ip == client_ip,
    ).first()

    return {
        "id": excuse.id,
        "text": excuse.text,
        "created_at": excuse.created_at,
        "lab_number": excuse.lab_number,
        "upvotes": excuse.upvotes,
        "downvotes": excuse.downvotes,
        "repo_id": excuse.repo_id,
        "user_vote": vote.direction if vote else None,
    }


@app.post("/api/excuses/{excuse_id}/vote", response_model=ExcuseResponse)
def vote_excuse(excuse_id: int, vote: VoteRequest, request: Request, db: Session = Depends(get_db)):
    """Vote on an excuse — one vote per IP per excuse. Re-voting switches your vote."""
    excuse = db.query(Excuse).filter(Excuse.id == excuse_id).first()
    if not excuse:
        raise HTTPException(status_code=404, detail="Excuse not found")

    # Get client IP
    client_ip = request.client.host

    # Check if already voted
    existing = db.query(Vote).filter(
        Vote.excuse_id == excuse_id,
        Vote.voter_ip == client_ip,
    ).first()

    if existing:
        if existing.direction == vote.direction:
            # Un-vote: remove the vote and the record
            if existing.direction == "up":
                excuse.upvotes = max(0, excuse.upvotes - 1)
            else:
                excuse.downvotes = max(0, excuse.downvotes - 1)
            db.delete(existing)
            db.commit()
        else:
            # Switch vote: decrement old, increment new
            if existing.direction == "up":
                excuse.upvotes = max(0, excuse.upvotes - 1)
            else:
                excuse.downvotes = max(0, excuse.downvotes - 1)
            if vote.direction == "up":
                excuse.upvotes += 1
            else:
                excuse.downvotes += 1
            existing.direction = vote.direction
            db.commit()
    else:
        # First vote
        if vote.direction == "up":
            excuse.upvotes += 1
        else:
            excuse.downvotes += 1
        new_vote = Vote(excuse_id=excuse_id, voter_ip=client_ip, direction=vote.direction)
        db.add(new_vote)
        db.commit()

    db.refresh(excuse)

    # Find the user's current vote
    user_vote = db.query(Vote).filter(
        Vote.excuse_id == excuse.id,
        Vote.voter_ip == client_ip,
    ).first()

    return {
        "id": excuse.id,
        "text": excuse.text,
        "created_at": excuse.created_at,
        "lab_number": excuse.lab_number,
        "upvotes": excuse.upvotes,
        "downvotes": excuse.downvotes,
        "repo_id": excuse.repo_id,
        "user_vote": user_vote.direction if user_vote else None,
    }


@app.delete("/api/excuses/{excuse_id}")
def delete_excuse(excuse_id: int, db: Session = Depends(get_db)):
    """Delete an excuse by ID."""
    excuse = db.query(Excuse).filter(Excuse.id == excuse_id).first()
    if not excuse:
        raise HTTPException(status_code=404, detail="Excuse not found")
    # Also delete associated votes
    db.query(Vote).filter(Vote.excuse_id == excuse_id).delete()
    db.delete(excuse)
    db.commit()
    return {"message": "Excuse deleted"}


# --- Saved Repositories Routes ---

@app.get("/api/repos", response_model=list[dict])
def list_repos(db: Session = Depends(get_db)):
    """List all saved GitHub repositories."""
    repos = db.query(SavedRepo).order_by(SavedRepo.created_at.desc()).all()
    import json
    result = []
    for repo in repos:
        techs = None
        if repo.technologies:
            try:
                techs = json.loads(repo.technologies)
            except json.JSONDecodeError:
                pass
        result.append({
            "id": repo.id,
            "github_url": repo.github_url,
            "repo_name": repo.repo_name,
            "description": repo.description,
            "lab_number": repo.lab_number,
            "technologies": techs,
            "created_at": repo.created_at,
        })
    return result


@app.post("/api/repos", response_model=dict)
def add_repo(request: AddRepoRequest, db: Session = Depends(get_db)):
    """Add a GitHub repository by URL and analyze it for excuse generation."""
    import json
    import urllib.request

    # Parse GitHub URL to extract owner and repo name
    url = request.github_url.rstrip("/")
    if not url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL. Must be https://github.com/...")

    # Extract owner/repo from URL
    parts = url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL format")

    owner, repo_name = parts[0], parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"

    # Fetch repo info from GitHub API
    try:
        req = urllib.request.Request(
            api_url,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "ExcuseForge"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            repo_data = json.loads(resp.read().decode())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch repository: {str(e)}")

    # Check if repo already exists
    existing = db.query(SavedRepo).filter(SavedRepo.github_url == url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Repository already saved")

    # Analyze repo for technologies
    desc = (repo_data.get("description") or "").lower()
    tech_keywords = {
        "docker": "docker" in desc or "container" in desc,
        "telegram": "telegram" in desc or "bot" in desc,
        "rest": "rest" in desc or "restful" in desc or "api" in desc or "fastapi" in desc,
        "frontend": "front" in desc or "front-end" in desc or "html" in desc,
        "testing": "test" in desc,
        "data_pipeline": "data pipeline" in desc or "etl" in desc or "analytics" in desc,
        "agent": "agent" in desc or "ai agent" in desc,
        "database": "database" in desc or "sql" in desc or "postgres" in desc or "sqlite" in desc,
        "deploy": "deploy" in desc or "vm" in desc or "linux" in desc,
        "ci_cd": "ci/cd" in desc or "ci cd" in desc or "pipeline" in desc,
        "workflow": "workflow" in desc or "orchestration" in desc,
        "evaluation": "evaluation" in desc or "benchmark" in desc,
    }
    # Auto-detect based on lab number
    lab_num = request.lab_number
    if lab_num:
        if lab_num == 2:
            tech_keywords["deploy"] = True
            tech_keywords["linux"] = True
            tech_keywords["docker"] = True
        elif lab_num == 3:
            tech_keywords["rest"] = True
            tech_keywords["database"] = True
            tech_keywords["testing"] = True
        elif lab_num == 4:
            tech_keywords["frontend"] = True
            tech_keywords["testing"] = True
            tech_keywords["agent"] = True
        elif lab_num == 5:
            tech_keywords["data_pipeline"] = True
            tech_keywords["database"] = True
        elif lab_num == 6:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
        elif lab_num == 7:
            tech_keywords["telegram"] = True
            tech_keywords["bot"] = True
        elif lab_num == 8:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
        elif lab_num == 9:
            tech_keywords["agent"] = True
            tech_keywords["ai"] = True
            tech_keywords["workflow"] = True
            tech_keywords["evaluation"] = True

    technologies = [k for k, v in tech_keywords.items() if v]

    saved_repo = SavedRepo(
        github_url=url,
        repo_name=repo_data.get("name", f"{owner}/{repo_name}"),
        description=repo_data.get("description"),
        lab_number=request.lab_number,
        technologies=json.dumps(technologies),
    )
    db.add(saved_repo)
    db.commit()
    db.refresh(saved_repo)

    techs = json.loads(saved_repo.technologies)
    return {
        "id": saved_repo.id,
        "github_url": saved_repo.github_url,
        "repo_name": saved_repo.repo_name,
        "description": saved_repo.description,
        "lab_number": saved_repo.lab_number,
        "technologies": techs,
        "created_at": saved_repo.created_at,
    }


@app.delete("/api/repos/{repo_id}")
def delete_repo(repo_id: int, db: Session = Depends(get_db)):
    """Remove a saved GitHub repository."""
    repo = db.query(SavedRepo).filter(SavedRepo.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    db.delete(repo)
    db.commit()
    return {"message": "Repository removed"}


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
