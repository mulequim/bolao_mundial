import streamlit as st
from db_manager import DBManager

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    db = DBManager()  # cria conexão
    if db.test_connection():
        st.success("🎉 Teste concluído! Conexão funcionando!")
    else:
        st.error("❌ Conexão criada, mas teste falhou.")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
