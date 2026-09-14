from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.chatbot import AnalyticsChatbot


ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="VibePlay Recommender API", version="1.0.0")
model = joblib.load(ROOT / "artifacts" / "model.joblib")
bot = AnalyticsChatbot(ROOT / "dashboard" / "assets" / "dashboard_data.json")


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get("/health")
def health():
    return {"status": "ok", "model": "hybrid-v1"}


@app.get("/recommend/{user_id}")
def recommend(user_id: str, n: int = 10):
    if n < 1 or n > 30:
        raise HTTPException(400, "n must be between 1 and 30")
    try:
        return {"user_id": user_id, "recommendations": model.recommend(user_id, n).to_dict("records")}
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/cold-start")
def cold_start(genres: str, n: int = 10):
    selected = [g.strip() for g in genres.split(",") if g.strip()]
    if not selected:
        raise HTTPException(400, "Provide comma-separated genres")
    return {"genres": selected, "recommendations": model.cold_start(selected, n).to_dict("records")}


@app.post("/chat")
def chat(payload: ChatRequest):
    return bot.answer(payload.question)

