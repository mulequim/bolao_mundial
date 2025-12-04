# db_manager.py
import streamlit as st

class DBManager:
    def __init__(self):
        try:
            # Conecta usando o bloco [connections.postgresql] do secrets
            self.conn = st.connection("postgresql", type="sql")

            # Teste simples
            result = self.conn.query("SELECT 1 AS ok;")
            st.success("✅ Conectado ao PostgreSQL com sucesso via st.connection!")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()
