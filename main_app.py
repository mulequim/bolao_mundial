import streamlit as st
from db_manager import DBManager

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    db = DBManager()              # cria conexão
    db.test_connection()          # testa a conexão
    st.success("🎉 Teste concluído! Conexão funcionando!")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
