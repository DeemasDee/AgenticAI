# streamlit_app.py
import streamlit as st
import requests

st.set_page_config(page_title="Agentic AI", layout="centered")
st.title("Agentic AI")
st.write("👋 Halo! Ini antarmuka frontend dengan Streamlit.")

# Coba panggil backend FastAPI jika sudah running
try:
    res = requests.get("https://your-fastapi-backend-url/hello")  # ubah URL sesuai hosting FastAPI
    if res.status_code == 200:
        st.success(f"FastAPI says: {res.json()['message']}")
    else:
        st.error("Gagal memanggil API FastAPI")
except Exception as e:
    st.warning("API tidak dapat diakses. Jalankan backend FastAPI secara terpisah.")
    st.code(str(e))
