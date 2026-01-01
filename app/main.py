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
        # Write to buffer
        buffer = io.BytesIO()
        sf.write(buffer, np.array(wav_data), 24000, format='WAV')
        # 2. Get the raw bytes directly
        audio_bytes = buffer.getvalue() 
        buffer.close()

        # 3. Return as a standard Response (Swagger handles this perfectly)
        return Response(content=audio_bytes, media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=story.wav"})

    except Exception as e:
        return {"error": str(e)}