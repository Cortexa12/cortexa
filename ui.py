import streamlit as st
import requests
import os
from supabase import create_client

# ===== SUPABASE =====
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

st.set_page_config(page_title="Cortexa", page_icon="🧠")

# ===== AUTH STATE =====
if "user" not in st.session_state:
    st.session_state.user = None

# ===== LOGIN =====
if st.session_state.user is None:
    st.title("🧠 Cortexa")
    st.write("Вход по email (magic link)")

    email = st.text_input("Email")
    if st.button("Получить ссылку для входа"):
        supabase.auth.sign_in_with_otp({"email": email})
        st.success("Проверь почту и перейди по ссылке для входа")

    st.stop()

# ===== MAIN UI =====
user = st.session_state.user
user_id = user.id

st.markdown(f"👤 **Вы вошли как:** {user.email}")
st.divider()

decision = st.text_area(
    "Опиши решение или ситуацию",
    height=160
)

if st.button("🔍 Проанализировать"):
    if not decision.strip():
        st.warning("Опиши ситуацию")
    else:
        with st.spinner("Cortexa думает..."):
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

        st.subheader("⚠️ Риски")
        for r in data.get("key_risks", []):
            st.write("-", r)

        st.subheader("🕳️ Слепое пятно")
        st.write(data.get("blind_spot"))

        st.subheader("🧠 Анализ")
        st.write(data.get("analysis"))
