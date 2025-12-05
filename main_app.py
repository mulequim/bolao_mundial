from db_manager import DBManager
import streamlit as st

db = DBManager()

if db.test_connection():
    st.success("Conexão com Supabase funcionando!")
else:
    st.error("Falha na conexão.")
