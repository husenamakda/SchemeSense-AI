from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import (
    analyze_user,
    generate_recommendation,
    ask_llm,
    chat_with_user,
)


router = APIRouter()


# ============================================================
# REQUEST MODELS
# ============================================================

class TextRequest(BaseModel):
    text: str


class RecommendationRequest(BaseModel):
    text: str
    profile: dict
    eligible_schemes: list
    best_scheme: dict | None = None


class ChatRequest(BaseModel):
    question: str
    profile: dict | None = None
    eligible_schemes: list | None = None


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "message": "SchemeSense AI API is running!"
    }


# ============================================================
# FAST ANALYSIS
# ============================================================

@router.post("/analyze")
def analyze(request: TextRequest):

    return analyze_user(
        request.text
    )


# ============================================================
# AI RECOMMENDATION
# ============================================================

@router.post("/recommend")
def recommend(
    request: RecommendationRequest
):

    recommendation = generate_recommendation(
        user_text=request.text,
        profile=request.profile,
        schemes=request.eligible_schemes,
        best_scheme=request.best_scheme
    )

    return {
        "answer": recommendation
    }


# ============================================================
# GENERAL RAG CHAT
# ============================================================

@router.post("/ask")
def ask(request: TextRequest):

    answer = ask_llm(
        request.text
    )

    return {
        "answer": answer
    }


# ============================================================
# FOLLOW-UP CHAT
# ============================================================

@router.post("/chat")
def chat(request: ChatRequest):

    answer = chat_with_user(
        question=request.question,
        profile=request.profile,
        eligible_schemes=request.eligible_schemes or []
    )

    return {
        "answer": answer
    }