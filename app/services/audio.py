import soundfile as sf

def get_audio_duration(path: str) -> float:
    with sf.SoundFile(path) as f:
        return len(f) / f.samplerate
