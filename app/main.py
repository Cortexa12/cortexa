from fastapi import FastAPI
from pydantic import BaseModel
from app.decision_engine import run_decision_engine

app = FastAPI(title="Cortexa API")

class DecisionRequest(BaseModel):
    decision: str

@app.post("/decide")
def decide(req: DecisionRequest):
    return {"result": run_decision_engine(req.decision)}

@app.get("/")
def root():
    return {"status": "Cortexa is running"}
