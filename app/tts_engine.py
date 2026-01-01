# tts_engine.py
import torch
import contextlib
from TTS.api import TTS


class TTSService:
    def __init__(self):
        print("Loading XTTS v2... please wait.")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # This context manager temporarily disables the strict weight check 
        # just for the duration of the model loading.
        with torch.serialization.safe_globals([]): # You can leave this empty
            # We use a trick: bypass the new default by setting weights_only=False
            # if the library allows, or use the environment variable fix below.
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
        print(f"Model loaded successfully on {device}!")

    def generate_speech(self, text, speaker_wav, language="en"):
        print(f"DEBUG: Attempting TTS with voice: {speaker_wav}")
        print(f"DEBUG: Text length: {len(text)}")
        
        # Force the model to use the absolute path
        import os
        abs_path = os.path.abspath(speaker_wav)
        
        wav = self.tts.tts(
            text=text,
            speaker_wav=abs_path,
            language=language
        )
        
        print(f"DEBUG: Generated waveform length: {len(wav)}")
        return wav