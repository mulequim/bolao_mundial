# db_manager.py
import streamlit as st

class DBManager:

    def __init__(self):
        try:
            # Conexão correta — Streamlit Cloud já usa o secrets automaticamente
            self.conn = st.connection("postgresql")

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    def test_connection(self):
        try:
            df = self.conn.query("SELECT 1 as ok;")
            return True
        except Exception as e:
            st.error(f"Erro no teste de conexão: {e}")
            return False
