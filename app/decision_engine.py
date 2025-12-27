import os
from supabase import create_client
from langchain_openai import ChatOpenAI

# ================= DEBUG ENV =================
print("=== CORTEXA SUPABASE ENV DEBUG ===")
print("SUPABASE_URL =", os.getenv("SUPABASE_URL"))
print(
    "SUPABASE_ANON_KEY =",
    "SET" if os.getenv("SUPABASE_ANON_KEY") else "MISSING"
)
print("=================================")

# ================= SUPABASE =================
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
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

ПРОФИЛЬ:
Роль: {profile.get("role", "не указана")}
Бизнес: {profile.get("business", "не указан")}
Страна: {profile.get("country", "не указана")}
Стиль риска: {profile.get("risk_style", "умеренный")}

ИСТОРИЯ ПРЕДЫДУЩИХ РЕШЕНИЙ:
{history}

ТЕКУЩАЯ СИТУАЦИЯ:
{decision}

Дай ответ СТРОГО в JSON со структурой:
- score (0–100)
- verdict
- risk_level
- key_risks (list)
- scenarios (A/B/C)
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
