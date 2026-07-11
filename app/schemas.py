"""
Pydantic schemas — define the shape of API requests and responses.
"""
from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class EmailIngest(BaseModel):
    """What the client sends in to ingest a new email."""
    sender: str = Field(..., examples=["boss@company.com"])
    subject: str = Field(..., examples=["Urgent: Q3 report needed by Friday"])
    body: str = Field(..., examples=["Hi, can you send me the Q3 report by end of day Friday? It's urgent."])
    received_at: Optional[datetime] = None


class DeadlineOut(BaseModel):
    text: str
    date: Optional[str] = None


class EmailOut(BaseModel):
    """What the API returns after processing an email."""
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime

    category: str
    priority_score: float
    summary: str
    action_items: List[str]
    deadlines: List[Dict]
    keywords: List[str]

    processed_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_emails: int
    by_category: Dict[str, int]
    avg_priority_score: float
    high_priority_count: int
    upcoming_deadlines: List[Dict]
