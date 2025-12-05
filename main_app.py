# main_app.py
import streamlit as st
from db_manager import DBManager

st.set_page_config(page_title="Teste Supabase", layout="centered")
st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    db = DBManager()
    if db.test_connection():
        st.success("🎉 Teste concluído! Conexão funcionando!")
    else:
        st.error("❌ Falha no teste de conexão.")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
