from fastapi import FastAPI

app = FastAPI(title="Story TTS API")

@app.get("/health")
def health():
    return {"status": "ok"}
