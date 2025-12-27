import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/decide"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Cortexa",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= GLOBAL STYLE =================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2.5rem;
    max-width: 1100px;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.stButton > button {
    background-color: #4F46E5;
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.6rem;
    border: none;
    font-weight: 600;
    font-size: 15px;
}

.stButton > button:hover {
    background-color: #4338CA;
}

section[data-testid="stSidebar"] {
    background-color: #0F172A;
}

section[data-testid="stSidebar"] * {
    color: #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "history" not in st.session_state:
    st.session_state.history = []

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Фаундер",
        "stage": "Ранний этап",
        "risk": "Умеренный",
        "horizon": "6–12 месяцев",
        "finance": "Средняя"
    }

# ================= SIDEBAR =================
st.sidebar.title("🧠 Cortexa")
st.sidebar.caption("Decision Intelligence")

st.sidebar.markdown("### 👤 Профиль")

name = st.sidebar.text_input("Имя", st.session_state.profile["name"])

stage = st.sidebar.selectbox(
    "Стадия бизнеса",
    ["Идея", "Ранний этап", "Рост", "Стабильный бизнес"],
    index=["Идея", "Ранний этап", "Рост", "Стабильный бизнес"]
    .index(st.session_state.profile["stage"])
)

risk = st.sidebar.selectbox(
    "Стиль риска",
    ["Осторожный", "Умеренный", "Агрессивный"],
    index=["Осторожный", "Умеренный", "Агрессивный"]
    .index(st.session_state.profile["risk"])
)

horizon = st.sidebar.selectbox(
    "Горизонт решений",
    ["1–3 месяца", "6–12 месяцев", "1–3 года"],
    index=["1–3 месяца", "6–12 месяцев", "1–3 года"]
    .index(st.session_state.profile["horizon"])
)

finance = st.sidebar.selectbox(
    "Финансовая чувствительность",
    ["Низкая", "Средняя", "Высокая"],
    index=["Низкая", "Средняя", "Высокая"]
    .index(st.session_state.profile["finance"])
)

if st.sidebar.button("💾 Сохранить профиль"):
    st.session_state.profile = {
        "name": name,
        "stage": stage,
        "risk": risk,
        "horizon": horizon,
        "finance": finance
    }
    st.sidebar.success("Профиль сохранён")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗂 История решений")

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history)):
        st.sidebar.markdown(f"{len(st.session_state.history)-i}. {item['title']}")
else:
    st.sidebar.caption("Пока нет решений")

# ================= MAIN =================
st.title("Cortexa")
st.caption("AI-партнёр для принятия бизнес-решений")

st.markdown("### Прими решение до того, как рынок примет его за тебя")

decision = st.text_area(
    "",
    height=150,
    placeholder="Напиши, какое решение ты хочешь принять. Cortexa разберёт его по рискам и сценариям…"
)

analyze = st.button("Принять решение →")

# ================= LOGIC =================
if analyze and decision.strip():
    profile_context = (
        f"Профиль пользователя:\n"
        f"- Имя: {st.session_state.profile['name']}\n"
        f"- Стадия бизнеса: {st.session_state.profile['stage']}\n"
        f"- Стиль риска: {st.session_state.profile['risk']}\n"
        f"- Горизонт решений: {st.session_state.profile['horizon']}\n"
        f"- Финансовая чувствительность: {st.session_state.profile['finance']}\n\n"
        f"Решение:\n{decision}"
    )

    with st.spinner("Cortexa анализирует…"):
        try:
            response = requests.post(
                API_URL,
                json={"decision": profile_context},
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()["result"]
                score = data.get("score", 50)

                # ===== RESULT HEADER =====
                st.markdown("## Итог решения")

                risk_icon = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
                st.markdown(f"### {risk_icon} Decision Score: {score}/100")
                st.progress(score / 100)

                st.markdown("### 🧭 Вердикт")
                st.info(data.get("verdict", "—"))

                # ===== DETAILS =====
                with st.expander("📊 Детальный анализ", expanded=False):

                    st.markdown("**Анализ**")
                    st.write(data.get("analysis", ""))

                    st.markdown("**Ключевые риски**")
                    for r in data.get("key_risks", []):
                        st.markdown(f"- {r}")

                    st.markdown("**Сценарии**")
                    for key, sc in data.get("scenarios", {}).items():
                        st.markdown(
                            f"- **Сценарий {key} ({int(sc['probability'] * 100)}%)** — {sc['description']}"
                        )

                    st.markdown("**Слепое пятно**")
                    st.warning(data.get("blind_spot", ""))

                st.session_state.history.append({
                    "title": decision[:50] + "…",
                    "data": data
                })

            else:
                st.error("Ошибка ответа от Cortexa")

        except requests.exceptions.RequestException:
            st.error("Нет соединения с Cortexa API")

# ================= FOOTER =================
st.markdown("---")
st.caption("Cortexa • Decision Intelligence SaaS • v1.2")
