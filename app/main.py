from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.decision_engine import run_decision_engine

# ---------------- APP ----------------
app = FastAPI(title="Cortexa Backend")

# ---------------- RATE LIMIT ----------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Слишком частые запросы",
            "message": "Пожалуйста, подождите 20 секунд перед следующим анализом."
        },
    )

# ---------------- MODELS ----------------
class DecisionRequest(BaseModel):
    decision: str
    user_id: str | None = "anonymous"

# ---------------- HEALTH ----------------
@app.get("/")
def health():
    return {"status": "ok", "service": "cortexa-backend"}

# ---------------- DECISION ----------------
@app.post("/decide")
@limiter.limit("1/20 seconds")
def decide(data: DecisionRequest):
    try:
        return run_decision_engine(
            decision=data.decision,
            user_id=data.user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
