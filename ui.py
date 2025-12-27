import streamlit as st
import requests
import os
from supabase import create_client

# ===== CONFIG =====
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(page_title="Cortexa", page_icon="🧠")

# ===== SESSION INIT =====
if "user" not in st.session_state:
    st.session_state.user = None

# ===== RESTORE SESSION FROM SUPABASE =====
if st.session_state.user is None:
    session = supabase.auth.get_session()
    if session and session.user:
        st.session_state.user = session.user

# ===== LOGIN SCREEN =====
if st.session_state.user is None:
    st.title("🧠 Cortexa")
    st.write("Вход по email (magic link)")

    email = st.text_input("Email")
    if st.button("Получить ссылку для входа"):
        supabase.auth.sign_in_with_otp({"email": email})
        st.success("Проверь почту и перейди по ссылке для входа")

    st.stop()

# ===== LOGGED IN =====
user = st.session_state.user
user_id = user.id

st.markdown(f"👤 **Вы вошли как:** {user.email}")
st.divider()

# ===== DECISION UI =====
decision = st.text_area(
    "Опиши решение или ситуацию",
    height=160
)

if st.button("🔍 Проанализировать"):
    if not decision.strip():
        st.warning("Опиши ситуацию")
    else:
        with st.spinner("Cortexa думает стратегически..."):
            response = requests.post(
                BACKEND_URL,
                json={
                    "decision": decision,
                    "user_id": user_id
                },
                timeout=120
            )
            data = response.json()

        st.subheader("🧭 Вердикт")
        st.write(data.get("verdict"))

        st.subheader("📊 Score")
        st.write(data.get("score"))

        st.subheader("⚠️ Ключевые риски")
        for r in data.get("key_risks", []):
            st.write("•", r)

        st.subheader("🕳️ Слепое пятно")
        st.write(data.get("blind_spot"))

        st.subheader("🧠 Глубокий анализ")
        st.write(data.get("analysis"))
