import streamlit as st
import db_manager as db

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    conn = db.get_conn()
    conn.query("SELECT 1;")
    st.success("🎉 Teste concluído! Conexão funcionando!")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
