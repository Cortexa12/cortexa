from fastapi import FastAPI
from pydantic import BaseModel
from app.decision_engine import run_decision_engine

app = FastAPI()

class DecisionRequest(BaseModel):
    decision: str
    user_id: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/decide")
def decide(req: DecisionRequest):
    result = run_decision_engine(
        decision=req.decision,
        user_id=req.user_id
    )

    # 🔴 ГАРАНТИЯ JSON
    if result is None:
        return {
            "error": "Decision engine returned nothing"
        }

    return result
