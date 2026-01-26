from fastapi import FastAPI
from app.api.stories import router as stories_router
from app.api.voices import router as voices_router

app = FastAPI(title="Story Teller API")
app.include_router(stories_router)
app.include_router(voices_router)

@app.get("/health")
def health():
    return {"status": "ok"}