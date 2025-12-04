import streamlit as st
from db_manager import DBManager

st.title("Teste de Conexão com PostgreSQL (Supabase)")

try:
    db = DBManager()
    st.success("✅ Conectado com sucesso ao banco PostgreSQL!")
except Exception as e:
    st.error(f"❌ Falha ao conectar: {e}")
    st.stop()

st.subheader("Usuários cadastrados:")
users = db.get_users_for_auth()

st.write(users)
