from fastapi import FastAPI
from pydantic import BaseModel
from app.decision_engine import run_decision_engine

app = FastAPI(
    title="Cortexa Backend",
    description="Decision Intelligence Engine",
    version="1.0.0"
)

# ===== Request schema =====
class DecisionRequest(BaseModel):
    decision: str
    user_id: str

# ===== Health check =====
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "cortexa-backend"
    }

# ===== Main decision endpoint =====
@app.post("/decide")
def decide(request: DecisionRequest):
    try:
        result = run_decision_engine(
            decision=request.decision,
            user_id=request.user_id
        )

        # Гарантируем JSON даже если что-то пошло не так
        if result is None:
            return {
                "error": "Decision engine returned empty result"
            }

        # Если вдруг вернулась строка — оборачиваем
        if isinstance(result, str):
            return {
                "analysis": result
            }

        return result

    except Exception as e:
        # НИКОГДА не возвращаем пустоту
        return {
            "error": "Backend exception",
            "details": str(e)
        }
