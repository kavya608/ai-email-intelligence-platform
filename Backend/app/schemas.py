from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class EmailIngestRequest(BaseModel):
    sender: str
    subject: Optional[str] = None
    body: str


class EmailResponse(BaseModel):
    id: int
    sender: str
    subject: Optional[str]
    body: str
    category: Optional[str]
    priority_score: Optional[int]
    summary: Optional[str]
    action_items: Optional[str]
    deadline: Optional[datetime]
    keywords: Optional[str]
    entities: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EmailReplyRequest(BaseModel):
    subject: str
    body: str
    tone: str = "professional"


class EmailReplyResponse(BaseModel):
    reply: str