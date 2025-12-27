import datetime

# ================= CORE FREE ENGINE =================

def run_decision_engine(decision: str, user_id: str):
    """
    Cortexa Free Mode
    Стратегический анализ без LLM
    """

    decision_lower = decision.lower()

    # ---------- БАЗОВЫЕ ЭВРИСТИКИ ----------
    risk_factors = []
    score = 70

    if any(word in decision_lower for word in ["аренда", "кредит", "долг", "заем"]):
        risk_factors.append("Финансовая нагрузка")
        score -= 10

    if any(word in decision_lower for word in ["команда", "перегруж", "не хватает людей"]):
        risk_factors.append("Операционная перегрузка")
        score -= 10

    if any(word in decision_lower for word in ["вторая", "масштаб", "расширение"]):
        risk_factors.append("Риск преждевременного масштабирования")
        score -= 10

    if any(word in decision_lower for word in ["нестабиль", "непонятно", "нет данных"]):
        risk_factors.append("Недостаток данных")
        score -= 10

    score = max(30, min(score, 85))

    # ---------- СЦЕНАРИИ ----------
    scenarios = {
        "A": {
            "title": "Консервативный сценарий",
            "description": "Фокус на стабилизации текущей модели без масштабирования.",
            "probability": 0.4
        },
        "B": {
            "title": "Умеренный рост",
            "description": "Ограниченное тестирование гипотез с контролем затрат.",
            "probability": 0.4
        },
        "C": {
            "title": "Агрессивное расширение",
            "description": "Рост без подтверждённой экономики может привести к потерям.",
            "probability": 0.2
        }
    }

    # ---------- ВЕРДИКТ ----------
    if score >= 75:
        verdict = "Решение выглядит обоснованным, при условии контролируемых рисков."
        risk_level = "low"
    elif score >= 55:
        verdict = "Решение требует корректировки и дополнительной проверки ключевых допущений."
        risk_level = "medium"
    else:
        verdict = "Решение несёт повышенные риски и требует пересмотра."
        risk_level = "high"

    # ---------- СЛЕПОЕ ПЯТНО ----------
    blind_spot = (
        "Недостаточно количественных метрик: маржа, CAC, "
        "нагрузка на команду, срок окупаемости."
    )

    # ---------- АНАЛИЗ ----------
    analysis = (
        "Анализ выполнен в Free Mode Cortexa на основе "
        "бизнес-эвристик, сценарного мышления и оценки рисков. "
        "Для более глубокого стратегического анализа доступен Pro Mode."
    )

    return {
        "score": score,
        "verdict": verdict,
        "risk_level": risk_level,
        "key_risks": risk_factors,
        "scenarios": scenarios,
        "blind_spot": blind_spot,
        "analysis": analysis,
        "mode": "free",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
