from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Case(SQLModel, table=True):
    id: str = Field(primary_key=True)
    patient_name: str
    payer: str
    status: str = "uploaded"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    draft_text: Optional[str] = None
    citations: Optional[str] = None

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: str
    type: str = "generate_draft"
    status: str = "queued"
    attempts: int = 0
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
