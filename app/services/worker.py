from uuid import UUID
from pathlib import Path
import soundfile as sf
import traceback

from app.storage.memory import stories, chunks
from app.services.xtts import get_tts_model


AUDIO_DIR = Path("outputs")
AUDIO_DIR.mkdir(exist_ok=True)


def process_story_chunks(story_id: UUID, voice_path: str):
    tts = get_tts_model()

    for chunk in chunks[story_id]:
        chunk["status"] = "processing"

        try:
            # in XTTS v2, tts.tts() returns ONLY ONE value:
            wav = tts.tts(
                text=chunk["text"],
                speaker_wav=voice_path,
                language=stories[story_id]["language"],
            )
            sample_rate = tts.synthesizer.output_sample_rate

            output_path = AUDIO_DIR / f"{story_id}_{chunk['index']}.wav"

            sf.write(output_path, wav, sample_rate)

            chunk["audio_path"] = str(output_path)
            chunk["status"] = "ready"

        except Exception as e:
            chunk["status"] = "failed"
            chunk["error"] = str(e)
            print("XTTS ERROR:")
            traceback.print_exc()

    stories[story_id]["status"] = "ready"
