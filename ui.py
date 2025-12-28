import streamlit as st
import requests
import time

# ---------------- CONFIG ----------------
BACKEND_URL = "https://cortexa-backend-rdu1.onrender.com/decide"

st.set_page_config(
    page_title="Cortexa",
    page_icon="🧠",
    layout="centered"
)

# ---------------- STATE ----------------
if "busy" not in st.session_state:
    st.session_state.busy = False

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# ---------------- UI ----------------
st.title("🧠 Cortexa")
st.subheader("Стратегический анализ решений для фаундеров и бизнеса")

st.markdown(
    "Введите управленческое или бизнес-решение — "
    "Cortexa проанализирует риски, сценарии и слепые зоны."
)

decision = st.text_area(
    "Ваше решение",
    placeholder="Например: Стоит ли открывать вторую кофейню с высокой арендой?",
    height=120
)

# ---------------- BUTTON ----------------
button_disabled = st.session_state.busy

if st.button("🔍 Проанализировать", disabled=button_disabled):
    if not decision.strip():
        st.warning("Введите решение для анализа.")
    else:
        st.session_state.busy = True
        st.session_state.last_request_time = time.time()

        progress = st.progress(0)
        status = st.empty()

        try:
            status.info("🔍 Анализ контекста и формулировки решения…")
            progress.progress(20)
            time.sleep(0.8)

            status.info("⚠️ Оценка рисков и неопределённостей…")
            progress.progress(45)
            time.sleep(0.8)

            status.info("📊 Построение сценариев развития…")
            progress.progress(70)
            time.sleep(0.8)

            response = requests.post(
                BACKEND_URL,
                json={
                    "decision": decision,
                    "user_id": "anonymous"
                },
                timeout=60
            )

            progress.progress(100)

            if response.status_code == 200:
                data = response.json()

                st.success("✅ Анализ завершён")

                st.markdown("### 📌 Вердикт")
                st.write(f"**{data['verdict']}**")

                st.markdown("### 🎯 Оценка решения")
                st.metric("Score", data["score"])
                st.write(f"**Уровень риска:** {data['risk_level'].upper()}")

                if data["key_risks"]:
                    st.markdown("### ⚠️ Ключевые риски")
                    for risk in data["key_risks"]:
                        st.write(f"- {risk}")

                st.markdown("### 🔮 Сценарии")
                for key, scenario in data["scenarios"].items():
                    st.write(
                        f"**{key}. {scenario['title']}** "
                        f"({int(scenario['probability'] * 100)}%)"
                    )
                    st.write(scenario["description"])

                st.markdown("### 🕳️ Слепое пятно")
                st.write(data["blind_spot"])

                st.markdown("### 🧠 Анализ Cortexa")
                st.write(data["analysis"])

                if data.get("mode") == "free":
                    st.info("ℹ️ Анализ выполнен в Free Mode Cortexa")

            elif response.status_code == 429:
                st.warning(
                    "⏳ Слишком частые запросы.\n\n"
                    "Пожалуйста, подождите 20 секунд перед следующим анализом."
                )

            else:
                st.error("Ошибка сервера. Попробуйте позже.")

        except requests.exceptions.Timeout:
            st.error("⏱️ Сервер долго отвечает. Попробуйте ещё раз через минуту.")

        except Exception as e:
            st.error(f"Ошибка: {e}")

        finally:
            st.session_state.busy = False
            progress.empty()
            status.empty()

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Cortexa • Strategic Decision Intelligence")
