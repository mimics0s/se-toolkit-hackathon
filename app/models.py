"""Database models for ExcuseForge."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base


class Excuse(Base):
    __tablename__ = "excuses"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    lab_number = Column(Integer, nullable=True)  # V2: per-lab filter
    upvotes = Column(Integer, default=0)          # V2: voting
    downvotes = Column(Integer, default=0)        # V2: voting
