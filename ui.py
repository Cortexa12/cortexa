import streamlit as st
import requests

BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

st.set_page_config(
    page_title="Cortexa — Decision Intelligence",
    page_icon="🧠",
    layout="centered"
)

# ===== STYLES =====
st.markdown("""
<style>
.card {
    background-color: #0f172a;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 20px;
    border: 1px solid #1e293b;
}
.small {
    color: #94a3b8;
    font-size: 14px;
}
.verdict {
    font-size: 22px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown(
    """
    <h1 style="text-align:center;">🧠 Cortexa</h1>
    <p style="text-align:center; font-size:17px;">
    AI, который думает о последствиях, а не просто отвечает
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ===== INPUT =====
decision = st.text_area(
    "Опиши ситуацию или решение",
    placeholder=(
        "Например:\n"
        "Я управляю кофейней. Думаю открыть вторую точку с высокой арендой, "
        "но первая ещё не даёт стабильной прибыли."
    ),
    height=160
)

analyze = st.button("🔍 Проанализировать")

# ===== ACTION =====
if analyze:
    if not decision.strip():
        st.warning("⚠️ Опиши ситуацию, чтобы Cortexa могла проанализировать.")
    else:
        with st.spinner("Cortexa анализирует риски, сценарии и скрытые последствия..."):
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

        # ===== SCORE =====
        st.markdown(
            f"""
            <div class="card">
                <div class="small">📊 Decision Score</div>
                <h2>{data.get("score", 0)} / 100</h2>
                <div class="small">Оценка устойчивости и качества решения</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ===== VERDICT =====
        st.markdown(
            f"""
            <div class="card">
                <div class="small">🧭 Вердикт Cortexa</div>
                <div class="verdict">{data.get("verdict", "—").capitalize()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ===== RISKS =====
        st.markdown("<div class='card'><div class='small'>🚨 Ключевые риски</div>", unsafe_allow_html=True)
        for r in data.get("key_risks", []):
            st.markdown(f"- {r.capitalize()}")
        st.markdown("</div>", unsafe_allow_html=True)

        # ===== SCENARIOS =====
        st.markdown("<div class='card'><div class='small'>🔮 Возможные сценарии</div>", unsafe_allow_html=True)
        scenarios = data.get("scenarios", {})
        for key, s in scenarios.items():
            st.markdown(
                f"**Сценарий {key} ({int(s.get('probability',0)*100)}%)**  \n"
                f"{s.get('description','')}"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # ===== BLIND SPOT =====
        st.markdown(
            f"""
            <div class="card">
                <div class="small">🕳️ Слепое пятно</div>
                <p>{data.get("blind_spot", "—").capitalize()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ===== ANALYSIS =====
        st.markdown(
            f"""
            <div class="card">
                <div class="small">🧠 Развёрнутый анализ</div>
                <p>{data.get("analysis", "—")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()
st.caption("© Cortexa — Decision Intelligence for Founders")
