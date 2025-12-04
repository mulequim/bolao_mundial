import streamlit as st
from db_manager import get_conn

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    conn = get_conn()
    conn.query("SELECT 1;")   # teste simples
    st.success("🎉 Teste concluído! Banco conectado com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
