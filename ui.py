import streamlit as st
import requests
import os
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BACKEND_URL = "https://cortexa-h34l.onrender.com/decide"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(page_title="Cortexa", page_icon="🧠")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= AUTH =================
def auth_ui():
    st.title("🧠 Cortexa")
    st.write("Вход или регистрация")

    tab_login, tab_signup = st.tabs(["Вход", "Регистрация"])

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
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка входа: {e}")

    with tab_signup:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Пароль (мин. 6 символов)", type="password", key="signup_password")
        if st.button("Зарегистрироваться"):
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("Аккаунт создан. Теперь войдите.")
            except Exception as e:
                st.error(f"Ошибка регистрации: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

if st.session_state.user is None:
    auth_ui()
    st.stop()

user = st.session_state.user
user_id = user.id

# ================= LOAD PROFILE =================
profile_resp = supabase.table("profiles").select("*").eq("id", user_id).execute()
profile = profile_resp.data[0] if profile_resp.data else {}

# ================= SIDEBAR PROFILE =================
st.sidebar.title("👤 Профиль")

role = st.sidebar.selectbox(
    "Роль",
    ["Фаундер", "Предприниматель", "Менеджер"],
    index=["Фаундер", "Предприниматель", "Менеджер"].index(profile.get("role", "Фаундер"))
)

business = st.sidebar.text_input(
    "Тип бизнеса",
    value=profile.get("business", "")
)

country = st.sidebar.text_input(
    "Страна",
    value=profile.get("country", "")
)

risk_style = st.sidebar.selectbox(
    "Стиль риска",
    ["Консервативный", "Умеренный", "Агрессивный"],
    index=["Консервативный", "Умеренный", "Агрессивный"].index(
        profile.get("risk_style", "Умеренный")
    )
)

if st.sidebar.button("💾 Сохранить профиль"):
    if profile:
        supabase.table("profiles").update({
            "role": role,
            "business": business,
            "country": country,
            "risk_style": risk_style
        }).eq("id", user_id).execute()
    else:
        supabase.table("profiles").insert({
            "id": user_id,
            "role": role,
            "business": business,
            "country": country,
            "risk_style": risk_style
        }).execute()
    st.sidebar.success("Профиль сохранён")

# ================= MAIN UI =================
st.markdown(f"👤 **Вы вошли как:** {user.email}")
st.button("Выйти", on_click=logout)
st.divider()

decision = st.text_area(
    "Опиши решение или бизнес-ситуацию",
    height=160,
    placeholder="Например: стоит ли масштабировать бизнес при текущей марже?"
)

if st.button("🔍 Проанализировать"):
    if not decision.strip():
        st.warning("Опиши ситуацию")
    else:
        with st.spinner("Cortexa анализирует стратегически..."):
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
