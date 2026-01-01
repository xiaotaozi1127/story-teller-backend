from fastapi import FastAPI
import io
import numpy as np
import soundfile as sf
from fastapi import FastAPI, Form, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from app.tts_engine import TTSService

app = FastAPI(title="Story TTS API")
tts_service = TTSService()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate-story")
async def generate_story(
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