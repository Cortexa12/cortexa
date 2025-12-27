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
    layout="wide"
)

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

# ================= SIDEBAR =================
st.sidebar.title("👤 Профиль")

role = st.sidebar.selectbox(
    "Роль",
    ["Фаундер", "Предприниматель", "Менеджер"],
    index=["Фаундер", "Предприниматель", "Менеджер"].index(profile.get("role", "Фаундер"))
)

business = st.sidebar.text_input("Тип бизнеса", value=profile.get("business", ""))
country = st.sidebar.text_input("Страна", value=profile.get("country", ""))
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

st.sidebar.divider()
st.sidebar.button("🚪 Выйти", on_click=logout)

# ================= MAIN LAYOUT =================
col_main, col_history = st.columns([2, 1])

# ================= MAIN ANALYSIS =================
with col_main:
    st.markdown(f"👤 **Вы вошли как:** {user.email}")
    st.divider()

    decision = st.text_area(
        "Опиши решение или бизнес-ситуацию",
        height=170,
        placeholder="Например: стоит ли открывать вторую кофейню при высокой аренде?"
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

            # ===== SAFE RESPONSE HANDLING =====
            if response.status_code != 200:
                st.error(f"Ошибка сервера ({response.status_code})")
                st.code(response.text)
                st.stop()

            if not response.text or not response.text.strip():
                st.error("Сервер вернул пустой ответ")
                st.stop()

            try:
                data = response.json()
            except Exception:
                st.error("Сервер вернул не-JSON ответ")
                st.code(response.text)
                st.stop()

            st.subheader("🧭 Стратегический вердикт")
            st.write(data.get("verdict", "—"))

            st.subheader("📊 Оценка решения")
            st.write(data.get("score", "—"))

            st.subheader("⚠️ Ключевые риски")
            for r in data.get("key_risks", []):
                st.write("•", r)

            st.subheader("🕳️ Слепое пятно")
            st.write(data.get("blind_spot", "—"))

            st.subheader("🧠 Глубокий анализ")
            st.write(data.get("analysis", "—"))

# ================= HISTORY =================
with col_history:
    st.subheader("📚 История решений")

    history_resp = (
        supabase
        .table("decisions")
        .select("decision_text, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    history = history_resp.data or []

    if not history:
        st.info("Пока нет решений")
    else:
        for item in history:
            with st.expander(item["decision_text"][:60] + "..."):
                st.caption(f"🕒 {item['created_at']}")
                st.write(item["decision_text"])

st.divider()
st.caption("© Cortexa — Decision Intelligence for Founders")
