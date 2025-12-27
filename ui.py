import streamlit as st

st.set_page_config(page_title="Cortexa", page_icon="🧠")

st.title("🧠 Cortexa")
st.write("Если ты видишь этот текст — Streamlit UI работает.")

text = st.text_area("Напиши любой текст:")
if st.button("Проверка"):
    st.success(f"Ты написал: {text}")
