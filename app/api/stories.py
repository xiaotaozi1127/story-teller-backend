    
import io
from uuid import UUID, uuid4
import numpy as np
import soundfile as sf
from pathlib import Path
from fastapi import APIRouter, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from app.services.chunker import split_text
from app.services.worker import process_story_chunks
from app.tts_engine import TTSService
from app.storage.memory import chunks, stories
from app.schemas.story import ChunkInfo, StoryCreateResponse, StoryStatusResponse
from typing import Dict, List

router = APIRouter(prefix="/stories", tags=["stories"])
tts_service = TTSService()

@router.get("/{story_id}/chunks/{index}")
async def get_story_chunk_audio(story_id: UUID, index: int):
    # Story exists?
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")

    story_chunks = chunks.get(story_id)
    if not story_chunks:
        raise HTTPException(status_code=404, detail="No chunks found")

    # Index valid?
    if index < 0 or index >= len(story_chunks):
        raise HTTPException(status_code=404, detail="Invalid chunk index")

    chunk = story_chunks[index]

    # Chunk status handling
    if chunk["status"] == "pending" or chunk["status"] == "processing":
        raise HTTPException(status_code=409, detail="Chunk not ready")

    if chunk["status"] == "failed":
        raise HTTPException(status_code=500, detail="Chunk generation failed")

    audio_path = Path(chunk["audio_path"])

    if not audio_path.exists():
        raise HTTPException(status_code=500, detail="Audio file missing")

    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=audio_path.name,
    )

@router.get("/{story_id}", response_model=StoryStatusResponse)
async def get_story_status(story_id: UUID):
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")

    story = stories[story_id]
    story_chunks = chunks.get(story_id, [])

    completed = sum(1 for c in story_chunks if c["status"] == "ready")

    return StoryStatusResponse(
        story_id=story_id,
        status=story["status"],
        language=story["language"],
        total_chunks=story["total_chunks"],
        completed_chunks=completed,
        chunks=[
            ChunkInfo(index=c["index"], status=c["status"])
            for c in story_chunks
        ],
    )

@router.post("/long-story", response_model=StoryCreateResponse, status_code=202)
async def create_story(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    language: str = Form("en"),
    chunk_size: int = Form(300),
    voice: UploadFile = File(...)
):
    if len(text) > 30_000:
        raise HTTPException(status_code=400, detail="Text too long")
    if language not in ("en", "zh"):
        raise HTTPException(400, "Unsupported language")

    story_id = uuid4()
    voice_path = f"/tmp/{story_id}_voice.wav"

    with open(voice_path, "wb") as f:
        f.write(await voice.read())

    text_chunks = split_text(text, max_len=chunk_size)

    if not text_chunks:
        raise HTTPException(status_code=400, detail="No valid text chunks")

    # Save story metadata
    stories[story_id] = {
        "id": story_id,
        "status": "processing",
        "language": language,
        "total_chunks": len(text_chunks),
    }

    # Save chunk metadata
    chunks[story_id] = [
        {
            "index": i,
            "text": chunk,
            "status": "pending",
            "audio_path": None,
        }
        for i, chunk in enumerate(text_chunks)
    ]

    # Schedule background TTS (stub for now)
    background_tasks.add_task(
        process_story_chunks,
        story_id,
        voice_path
    )

    return StoryCreateResponse(
        story_id=story_id,
        status="processing",
        total_chunks=len(text_chunks),
    )

@router.post("/test-speech")
async def generate_speech(
    text: str = Form(...), 
    language: str = Form("en"),
    voice_sample: UploadFile = File(...)
):
    try:
        # Save the uploaded voice sample
        contents = await voice_sample.read()
        temp_voice_path = f"uploads/{voice_sample.filename}"
        with open(temp_voice_path, "wb") as f:
            f.write(contents)

        # Generate audio
        # Note: tts_service.tts returns a list of floats (the waveform)
        wav_data = tts_service.generate_speech(
            text=text, 
            speaker_wav=temp_voice_path, 
            language=language
        )
        # Convert to numpy and ensure it's float32
        audio_array = np.array(wav_data).astype(np.float32)
        
        buffer = io.BytesIO()
        # Write the numpy array
        sf.write(buffer, audio_array, 24000, format='WAV')
        buffer.seek(0)

        # 3. Return as a standard Response (Swagger handles this perfectly)
        return StreamingResponse(buffer, media_type="audio/wav")

    except Exception as e:
        return {"error": str(e)}