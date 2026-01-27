from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from uuid import uuid4
from datetime import datetime
import shutil
import os

from app.schemas.voice import Voice
from app.services.audio import get_audio_duration
from app.storage.memory import voices

router = APIRouter(prefix="/voices", tags=["voices"])

VOICE_DIR = "upload/voices"
os.makedirs(VOICE_DIR, exist_ok=True)


@router.post("", status_code=201)
async def create_voice(
    name: str = Form(...),
    language: str = Form("en"),
    voice: UploadFile = File(...)
):
    if not voice.filename:
        raise HTTPException(status_code=400, detail="Voice file required")

    if not voice.content_type.startswith("audio"):
        raise HTTPException(status_code=400, detail="Invalid audio file")

    voice_id = uuid4()
    file_path = os.path.join(VOICE_DIR, f"{voice_id}.wav")

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(voice.file, buffer)

    # Read duration
    try:
        duration = get_audio_duration(file_path)
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid audio format")

    # Validation rules (important for XTTS quality)
    if duration < 3:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Voice sample too short (min 3s)")

    if duration > 30:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Voice sample too long (max 30s)")

    voices[voice_id] = {
        "id": voice_id,
        "name": name,
        "language": language,
        "audio_path": file_path,
        "duration_sec": round(duration, 2),
        "created_at": datetime.now()
    }

    return {
        "voice_id": voice_id,
        "duration_sec": round(duration, 2),
    }

@router.get("", response_model=list[Voice])
async def list_voices():
    return voices.values()