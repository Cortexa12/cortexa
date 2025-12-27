import os
import json
from langchain_openai import ChatOpenAI
from supabase import create_client

# ================= SAFE SUPABASE =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ================= SAFE LLM =================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.65
)

SYSTEM_PROMPT = """
Ты — Cortexa, стратегический интеллект уровня инвестиционного комитета.

Отвечай СТРОГО в формате JSON без текста вне структуры.

ФОРМАТ:
{
  "score": number,
  "verdict": string,
  "risk_level": "low" | "medium" | "high",
  "key_risks": [string],
  "scenarios": {
    "A": {"title": string, "description": string, "probability": number},
    "B": {"title": string, "description": string, "probability": number},
    "C": {"title": string, "description": string, "probability": number}
  },
  "blind_spot": string,
  "analysis": string
}
"""

# ================= CORE =================
def run_decision_engine(decision: str, user_id: str):
    profile = {}
    history = []

    # ---- SAFE PROFILE LOAD ----
    if supabase:
        try:
            resp = (
                supabase
                .table("profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            profile = resp.data or {}
        except Exception:
            profile = {}

        try:
            mem = (
                supabase
                .table("decisions")
                .select("decision_text")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(3)
                .execute()
            )
            history = mem.data or []
        except Exception:
            history = []

    # ---- PROMPT ----
    user_prompt = f"""
ПРОФИЛЬ:
Роль: {profile.get("role", "не указана")}
Бизнес: {profile.get("business", "не указан")}
Стиль риска: {profile.get("risk_style", "умеренный")}

ИСТОРИЯ:
{history}

ТЕКУЩЕЕ РЕШЕНИЕ:
{decision}
"""

    # ---- SAFE LLM CALL ----
    try:
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])
        raw = response.content.strip()
        result = json.loads(raw)
    except Exception as e:
        result = {
            "score": 50,
            "verdict": "Недостаточно данных для уверенного стратегического решения.",
            "risk_level": "medium",
            "key_risks": ["Ограниченный контекст", "Высокая неопределённость"],
            "scenarios": {
                "A": {
                    "title": "Осторожный рост",
                    "description": "Постепенное тестирование гипотез без масштабирования.",
                    "probability": 0.4
                },
                "B": {
                    "title": "Сохранение статуса-кво",
                    "description": "Фокус на стабилизации текущего бизнеса.",
                    "probability": 0.4
                },
                "C": {
                    "title": "Преждевременное расширение",
                    "description": "Рост без подтверждённой модели может привести к убыткам.",
                    "probability": 0.2
                }
            },
            "blind_spot": "Не хватает количественных метрик (маржа, CAC, нагрузка команды).",
            "analysis": f"LLM fallback mode. Причина: {str(e)}"
        }

    # ---- SAFE SAVE MEMORY ----
    if supabase:
        try:
            supabase.table("decisions").insert({
                "user_id": user_id,
                "decision_text": decision,
                "result": result
            }).execute()
        except Exception:
            pass

    return result
