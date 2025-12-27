import streamlit as st
import requests
import os
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(
    page_title="Cortexa",
    page_icon="🧠",
    layout="centered"
)

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= AUTH UI =================
def auth_ui():
    st.title("🧠 Cortexa")
    st.write("Вход или регистрация")

    tab_login, tab_signup = st.tabs(["Вход", "Регистрация"])

    # -------- LOGIN --------
    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Пароль", type="password", key="login_password")

        if st.button("Войти"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = res.user
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Ошибка входа: {e}")

    # -------- SIGN UP --------
    with tab_signup:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input(
            "Пароль (минимум 6 символов)",
            type="password",
            key="signup_password"
        )

        if st.button("Зарегистрироваться"):
            try:
                res = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("Аккаунт создан. Теперь войдите во вкладке «Вход».")
            except Exception as e:
                st.error(f"Ошибка регистрации: {e}")

# ================= LOGOUT =================
def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.experimental_rerun()

# ================= MAIN FLOW =================
if st.session_state.user is None:
    auth_ui()
    st.stop()

# ================= LOGGED IN =================
user = st.session_state.user
user_id = user.id

st.markdown(f"👤 **Вы вошли как:** {user.email}")
st.button("Выйти", on_click=logout)
st.divider()

# ================= DECISION UI =================
decision = st.text_area(
    "Опиши решение или бизнес-ситуацию",
    height=170,
    placeholder=(
        "Например:\n"
        "Стоит ли открывать вторую кофейню с высокой арендой, "
        "если первая ещё не даёт стабильной прибыли?"
    )
)

if st.button("🔍 Проанализировать"):
    if not decision.strip():
        st.warning("Опиши ситуацию для анализа.")
    else:
        with st.spinner("Cortexa анализирует стратегически..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={
                        "decision": decision,
                        "user_id": user_id
                    },
                    timeout=120
                )
                data = response.json()
            except Exception as e:
                st.error(f"Ошибка соединения с сервером: {e}")
                st.stop()

        # ===== OUTPUT =====
        st.subheader("🧭 Вердикт")
        st.write(data.get("verdict", "—"))

        st.subheader("📊 Decision Score")
        st.write(data.get("score", "—"))

        st.subheader("⚠️ Ключевые риски")
        for r in data.get("key_risks", []):
            st.write("•", r)

        st.subheader("🔮 Сценарии")
        for k, s in data.get("scenarios", {}).items():
            st.write(f"**Сценарий {k} ({int(s.get('probability',0)*100)}%)**")
            st.write(s.get("description", ""))

        st.subheader("🕳️ Слепое пятно")
        st.write(data.get("blind_spot", "—"))

        st.subheader("🧠 Глубокий стратегический анализ")
        st.write(data.get("analysis", "—"))

st.divider()
st.caption("© Cortexa — Decision Intelligence for Founders")
