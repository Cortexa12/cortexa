import os
from supabase import create_client
from langchain_openai import ChatOpenAI

# ================= SUPABASE (SERVER MODE) =================
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# ================= LLM =================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4
)

# ================= CORE =================
def run_decision_engine(decision: str, user_id: str):
    # ---- Load profile ----
    profile_resp = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )
    profile = profile_resp.data or {}

    # ---- Load memory ----
    memory_resp = (
        supabase
        .table("decisions")
        .select("decision_text, result")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    history = memory_resp.data or []

    # ---- Prompt ----
    prompt = f"""
Ты — Cortexa, персональный AI для принятия решений.

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
• Роль: {profile.get("role", "не указана")}
• Бизнес: {profile.get("business", "не указан")}
• Страна: {profile.get("country", "не указана")}
• Стиль риска: {profile.get("risk_style", "умеренный")}

ПРЕДЫДУЩИЕ РЕШЕНИЯ:
{history}

ТЕКУЩАЯ СИТУАЦИЯ:
{decision}

Ответь СТРОГО в JSON:
- score
- verdict
- risk_level
- key_risks
- scenarios
- blind_spot
- analysis
"""

    result = llm.invoke(prompt).content

    # ---- Save memory ----
    supabase.table("decisions").insert({
        "user_id": user_id,
        "decision_text": decision,
        "result": result
    }).execute()

    return result
