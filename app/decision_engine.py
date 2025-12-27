import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# ===== MODELS =====
thinker = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.15
)

critic = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

speaker = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.35
)

# ===== PROMPTS =====

THINKING_PROMPT = """
Ты — стратегический аналитик.
Твоя задача — ПРОДУМАТЬ решение, но НЕ писать красиво.

Ответь строго структурировано:
- Что здесь на самом деле происходит?
- Где логическая ошибка пользователя?
- Какой риск он недооценивает?
- Чем это может закончиться в худшем случае?

Пиши сухо, без эмоций.
"""

CRITIC_PROMPT = """
Ты — жёсткий бизнес-критик.
Твоя задача — раскритиковать вывод аналитика.

Ответь:
- Где вывод слишком мягкий?
- Где нужно усилить давление?
- Что пользователь НЕ ХОЧЕТ слышать, но обязан?

Будь прямым.
"""

SPEAKER_PROMPT = """
Ты — Cortexa.
Ты — ИИ-партнёр фаундера.

Твоя задача — выдать ФИНАЛЬНЫЙ ответ пользователю.
Пиши как ChatGPT 5.2:

ОБЯЗАТЕЛЬНО:
- Развёрнутый вердикт (2–4 предложения)
- Человеческий язык
- Заглавные буквы
- Уместные эмодзи
- Давление аргументами
- Слепое пятно как удар в мышление

❗ Верни СТРОГО JSON (НИЧЕГО ВНЕ JSON):

{
  "verdict": "Развёрнутый вердикт",
  "score": 0-100,
  "risk_level": "low | medium | high",
  "key_risks": ["Риск 1", "Риск 2"],
  "scenarios": {
    "A": {"description": "...", "probability": 0.0},
    "B": {"description": "...", "probability": 0.0},
    "C": {"description": "...", "probability": 0.0}
  },
  "blind_spot": "Развёрнутое слепое пятно (2–3 предложения)",
  "analysis": "Связный анализ (5–7 предложений)"
}

Правила:
- Вероятности ≈ 1.0
- Score должен соответствовать тексту
- Если риск высокий — это должно чувствоваться
"""

# ===== ENGINE =====

def run_decision_engine(user_input: str) -> dict:
    # PASS 1 — THINKING
    thinking = thinker.invoke([
        {"role": "system", "content": THINKING_PROMPT},
        {"role": "user", "content": user_input}
    ]).content

    # PASS 2 — CRITIC
    critique = critic.invoke([
        {"role": "system", "content": CRITIC_PROMPT},
        {"role": "user", "content": thinking}
    ]).content

    # PASS 3 — FINAL SPEAK
    final_input = f"""
РЕШЕНИЕ ПОЛЬЗОВАТЕЛЯ:
{user_input}

ВНУТРЕННИЙ АНАЛИЗ:
{thinking}

КРИТИКА:
{critique}
"""

    final_response = speaker.invoke([
        {"role": "system", "content": SPEAKER_PROMPT},
        {"role": "user", "content": final_input}
    ]).content.strip()

    try:
        return json.loads(final_response)
    except json.JSONDecodeError:
        return {
            "verdict": "⚠️ Cortexa столкнулась с редкой логической перегрузкой. Это сигнал, что решение требует дополнительной декомпозиции.",
            "score": 50,
            "risk_level": "medium",
            "key_risks": [],
            "scenarios": {},
            "blind_spot": "Решение сформулировано слишком обобщённо, из-за чего часть ключевых рисков может быть скрыта.",
            "analysis": final_response
        }

