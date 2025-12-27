import streamlit as st
import requests

# ====== CONFIG ======
BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

st.set_page_config(
    page_title="Cortexa — Decision Intelligence",
    page_icon="🧠",
    layout="centered"
)

# ====== HEADER ======
st.markdown(
    """
    <h1 style="text-align:center;">🧠 Cortexa</h1>
    <p style="text-align:center; font-size:18px;">
    Decision Intelligence для фаундеров и бизнеса
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ====== INPUT ======
decision = st.text_area(
    "Опиши решение или дилемму 👇",
    placeholder=(
        "Пример:\n"
        "Стоит ли открывать вторую кофейню в районе с высокой арендой, "
        "если первая ещё не даёт стабильной прибыли?"
    ),
    height=150
)

analyze = st.button("🔍 Проанализировать")

# ====== ACTION ======
if analyze:
    if not decision.strip():
        st.warning("⚠️ Пожалуйста, опиши решение.")
    else:
        with st.spinner("Cortexa анализирует риски и сценарии..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"decision": decision},
                    timeout=120
                )
                data = response.json()
            except Exception as e:
                st.error(f"Ошибка соединения с сервером: {e}")
                st.stop()

        # ====== OUTPUT ======
        st.success("Анализ готов")

        # SCORE
        score = data.get("score", 0)
        st.subheader("📊 Decision Score")
        st.progress(score / 100)
        st.write(f"**{score} / 100**")

        # VERDICT
        st.subheader("🧭 Вердикт")
        st.markdown(f"**{data.get('verdict', '—').capitalize()}**")

        # RISK LEVEL
        st.subheader("⚠️ Уровень риска")
        st.write(data.get("risk_level", "—").capitalize())

        # KEY RISKS
        st.subheader("🚨 Ключевые риски")
        for r in data.get("key_risks", []):
            st.write(f"• {r.capitalize()}")

        # SCENARIOS
        st.subheader("🔮 Сценарии развития")
        scenarios = data.get("scenarios", {})
        for key, s in scenarios.items():
            st.markdown(
                f"**Сценарий {key} ({int(s.get('probability',0)*100)}%)**  \n"
                f"{s.get('description','')}"
            )

        # BLIND SPOT
        st.subheader("🕳️ Слепое пятно")
        st.write(data.get("blind_spot", "—").capitalize())

        # ANALYSIS
        st.subheader("🧠 Развёрнутый анализ")
        st.write(data.get("analysis", "—"))

st.divider()
st.caption("© Cortexa — AI Decision Intelligence for Founders")
