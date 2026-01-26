from uuid import UUID
from typing import Dict, List

from app.schemas.voice import Voice


stories: Dict[UUID, dict] = {}
chunks: Dict[UUID, List[dict]] = {}
voices: Dict[UUID, Voice] = {}
