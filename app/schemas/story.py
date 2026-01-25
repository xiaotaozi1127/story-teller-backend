from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class StoryCreateResponse(BaseModel):
    story_id: UUID
    status: str
    total_chunks: int


class ChunkInfo(BaseModel):
    index: int
    status: str
    progress_percentage: float


class StoryStatusResponse(BaseModel):
    story_id: UUID
    status: str
    title: str
    total_chunks: int
    completed_chunks: int
    chunks: List[ChunkInfo]

class StoryListItem(BaseModel):
    id: UUID
    status: str
    title: str
    language: str
    total_chunks: int
    progress_percentage: float
    total_duration_seconds: float
    created_at: datetime