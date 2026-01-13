from pydantic import BaseModel
from typing import List
from uuid import UUID


class StoryCreateResponse(BaseModel):
    story_id: UUID
    status: str
    total_chunks: int


class ChunkInfo(BaseModel):
    index: int
    status: str


class StoryStatusResponse(BaseModel):
    story_id: UUID
    status: str
    total_chunks: int
    completed_chunks: int
    chunks: List[ChunkInfo]
