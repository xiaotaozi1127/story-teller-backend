from TTS.api import TTS

_tts_model = None


def get_tts_model():
    global _tts_model
    if _tts_model is None:
        _tts_model = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False,
            gpu=False,  # set True if CUDA available
        )
    return _tts_model
