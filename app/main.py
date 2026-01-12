from fastapi import FastAPI
from app.api.stories import router as stories_router

app = FastAPI(title="Story TTS API")
app.include_router(stories_router)

@app.get("/health")
def health():
    return {"status": "ok"}