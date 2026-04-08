"""Database models for ExcuseForge."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database import Base


class Excuse(Base):
    __tablename__ = "excuses"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    lab_number = Column(Integer, nullable=True)  # V2: per-lab filter
    upvotes = Column(Integer, default=0)          # V2: voting
    downvotes = Column(Integer, default=0)        # V2: voting
    repo_id = Column(Integer, nullable=True)      # Link to saved repo that generated this excuse


class SavedRepo(Base):
    __tablename__ = "saved_repos"

    id = Column(Integer, primary_key=True, index=True)
    github_url = Column(String, nullable=False, unique=True)
    repo_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    lab_number = Column(Integer, nullable=True)
    technologies = Column(String, nullable=True)  # JSON string of tech list
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    excuse_id = Column(Integer, ForeignKey("excuses.id"), nullable=False)
    voter_ip = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # "up" or "down"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
