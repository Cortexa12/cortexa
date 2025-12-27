from fastapi import FastAPI
from pydantic import BaseModel
from app.decision_engine import run_decision_engine

app = FastAPI(title="Cortexa Backend")

# ===== REQUEST SCHEMA =====
class DecisionRequest(BaseModel):
    decision: str
    user_id: str

# ===== HEALTH CHECK =====
@app.get("/")
def root():
    return {"status": "Cortexa backend is running"}

# ===== MAIN ENDPOINT =====
@app.post("/decide")
def decide(req: DecisionRequest):
    try:
        result = run_decision_engine(
            decision=req.decision,
            user_id=req.user_id
        )
        return result  # 🔴 КРИТИЧНО: возвращаем JSON
    except Exception as e:
        return {
            "error": "Decision engine failed",
            "details": str(e)
        }
