"""
SQLAlchemy ORM models.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON

from app.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    # Raw email fields
    sender = Column(String(255), index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)

    # AI-derived intelligence
    category = Column(String(50), index=True)          # e.g. Urgent, Action Needed, Meeting, Informational, Spam-like
    priority_score = Column(Float, default=0.0)         # 0-100
    summary = Column(Text)                              # extractive summary
    action_items = Column(JSON, default=list)           # list of strings
    deadlines = Column(JSON, default=list)               # list of {"text": ..., "date": ...}
    keywords = Column(JSON, default=list)               # top keywords detected

    processed_at = Column(DateTime, default=datetime.utcnow)
