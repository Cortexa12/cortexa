import os
import json
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
    temperature=0.65
)

# ================= SYSTEM PERSONA =================
SYSTEM_PROMPT = """
Ты — Cortexa.

Ты — не чат-бот и не помощник.
Ты — персональный стратегический интеллект уровня инвестиционного комитета.

ТВОЙ СТИЛЬ:
• Говоришь уверенно, спокойно, структурировано
• Используешь заглавные буквы в заголовках
• Используешь эмодзи ТОЛЬКО в заголовках (умеренно)
• Никогда не отвечаешь коротко
• Всегда объясняешь «почему»

ТВОЯ ЦЕЛЬ:
Помочь пользователю принять качественное решение,
увидеть риски, сценарии и слепые зоны мышления.

ФОРМАТ ОТВЕТА — СТРОГО JSON:

{
  "score": number (0-100),
  "verdict": string,
  "risk_level": "low" | "medium" | "high",
  "key_risks": [string, string, ...],
  "scenarios": {
    "A": {"title": string, "description": string, "probability": number},
    "B": {"title": string, "description": string, "probability": number},
    "C": {"title": string, "description": string, "probability": number}
  },
  "blind_spot": string,
  "analysis": string
}

НЕ добавляй никакого текста вне JSON.
"""

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

    # ---- Build user prompt ----
    user_prompt = f"""
ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
• Роль: {profile.get("role", "не указана")}
• Бизнес: {profile.get("business", "не указан")}
• Страна: {profile.get("country", "не указана")}
• Стиль риска: {profile.get("risk_style", "умеренный")}

ИСТОРИЯ ПРЕДЫДУЩИХ РЕШЕНИЙ:
{history}

ТЕКУЩАЯ СИТУАЦИЯ:
{decision}
"""

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    content = response.content.strip()

    try:
        result_json = json.loads(content)
    except json.JSONDecodeError:
        result_json = {
            "score": 50,
            "verdict": "Недостаточно данных для уверенного решения.",
            "risk_level": "medium",
            "key_risks": ["Нечётко сформулирована ситуация"],
            "scenarios": {},
            "blind_spot": "Формулировка вопроса не раскрывает контекст полностью.",
            "analysis": content
        }

    # ---- Save memory ----
    supabase.table("decisions").insert({
        "user_id": user_id,
        "decision_text": decision,
        "result": result_json
    }).execute()

    return result_json

