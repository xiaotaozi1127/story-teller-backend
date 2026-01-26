from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class Voice(BaseModel):
    id: UUID
    name: str
    language: str
    audio_path: str
    duration_sec: float
    created_at: datetime
