    
import io
import logging
from datetime import datetime
from uuid import UUID, uuid4
import numpy as np
import soundfile as sf
from pathlib import Path
from fastapi import APIRouter, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from app.services.chunker import split_text_smart
from app.services.worker import process_story_chunks
from app.tts_engine import TTSService
from app.storage.memory import chunks, stories
from app.schemas.story import ChunkInfo, StoryCreateResponse, StoryStatusResponse, StoryListItem
from typing import Dict, List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories", tags=["stories"])
tts_service = TTSService()

@router.get("", response_model=list[StoryListItem])
def list_stories():
    logger.debug("GET stories endpoint received request")
    sorted_stories = sorted(
        stories.values(),
        key=lambda x: x.get("created_at", datetime.min),
        reverse=True,
    )
    
    result = []
    for story in sorted_stories:
        story_id = story["id"]
        story_chunks = chunks.get(story_id, [])
        
        # Calculate progress_percentage based on chunk progress
        if story_chunks and story["total_chunks"] > 0:
            total_progress = sum(c.get("progress", 0.0) for c in story_chunks)
            progress_percentage = (total_progress / story["total_chunks"]) * 100.0
        else:
            progress_percentage = 0.0
        
        result.append(
            StoryListItem(
                id=story["id"],
                status=story["status"],
                title=story.get("title", "Untitled story"),
                language=story["language"],
                total_chunks=story["total_chunks"],
                progress_percentage=round(progress_percentage, 2),
                total_duration_seconds=story.get("total_duration_seconds", 0.0),
                created_at=story["created_at"],
            )
        )
    
    return result

@router.get("/{story_id}/chunks/{index}")
async def get_story_chunk_audio(story_id: UUID, index: int):
    logger.debug(f"GET story chunk endpoint received request")
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
    logger.debug(f"GET story status endpoint received request for story_id: {story_id}")
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")

    story = stories[story_id]
    story_chunks = chunks.get(story_id, [])

    completed = sum(1 for c in story_chunks if c["status"] == "ready")

    # Calculate progress_percentage based on chunk progress
    if story_chunks and story["total_chunks"] > 0:
        total_progress = sum(c.get("progress", 0.0) for c in story_chunks)
        progress_percentage = (total_progress / story["total_chunks"]) * 100.0
    else:
        progress_percentage = 0.0

    return StoryStatusResponse(
        story_id=story_id,
        status=story["status"],
        title=story.get("title", "Untitled story"),
        language=story["language"],
        total_chunks=story["total_chunks"],
        total_duration_seconds=
            story.get("total_duration_seconds", 0.0),
        completed_chunks=completed,
        progress_percentage=round(progress_percentage, 2),
        chunks=[
            ChunkInfo(
                index=c["index"],
                status=c["status"],
                progress_percentage=c.get("progress", 0.0) * 100.0
            )
            for c in story_chunks
        ],
    )

@router.post("", response_model=StoryCreateResponse, status_code=202)
async def create_story(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    title: str = Form(""),
    language: str = Form("en"),
    chunk_size: int = Form(300),
    voice: UploadFile = File(...)
):
    logger.debug("POST /stories endpoint received request")
    logger.debug(f"Request parameters - language: {language}, chunk_size: {chunk_size}, voice filename: {voice.filename}")
    logger.debug(f"Text length: {len(text)} characters")
    logger.debug(f"Title provided: '{title}'")
    
    if len(text) > 30_000:
        raise HTTPException(status_code=400, detail="Text too long")
    if language not in ("en", "zh"):
        raise HTTPException(400, "Unsupported language")

    story_id = uuid4()
    voice_path = f"/tmp/{story_id}_voice.wav"

    with open(voice_path, "wb") as f:
        f.write(await voice.read())

    text_chunks = split_text_smart(text, max_len=chunk_size)

    if not text_chunks:
        raise HTTPException(status_code=400, detail="No valid text chunks")

    normalized_title = title.strip() or "Untitled story"

    # Save story metadata
    stories[story_id] = {
        "id": story_id,
        "status": "processing",
        "title": normalized_title,
        "language": language,
        "total_chunks": len(text_chunks),
        "created_at": datetime.utcnow(),
    }

    # Save chunk metadata
    chunks[story_id] = [
        {
            "index": i,
            "text": chunk,
            "status": "pending",
            "audio_path": None,
            "progress": 0.0,
        }
        for i, chunk in enumerate(text_chunks)
    ]

    # Schedule background TTS (stub for now)
    background_tasks.add_task(
        process_story_chunks,
        story_id,
        voice_path
    )

    logger.debug(f"Story created successfully - story_id: {story_id}, total_chunks: {len(text_chunks)}")
    
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