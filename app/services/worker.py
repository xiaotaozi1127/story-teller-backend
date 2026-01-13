import time
from app.storage.memory import chunks, stories
from uuid import UUID


def process_story_chunks(story_id: UUID, voice_path: str):
    for chunk in chunks[story_id]:
        chunk["status"] = "processing"

        # Simulate XTTS inference
        time.sleep(1)

        chunk["status"] = "ready"
        chunk["audio_path"] = f"/outputs/{story_id}_{chunk['index']}.wav"

    stories[story_id]["status"] = "ready"
