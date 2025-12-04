import streamlit as st
from db_manager import DBManager

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

db = DBManager()

st.success("🎉 Teste concluído!")
