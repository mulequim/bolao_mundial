# db_manager.py
import streamlit as st
import pandas as pd

class DBManager:
    def __init__(self):
        try:
            # Lê a config do secrets
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError("Configuração 'connections.postgresql' não encontrada em st.secrets.")

            conf = st.secrets["connections"]["postgresql"]

            # Cria a conexão corretamente
            self.conn = st.connection(
                "postgresql",
                type="sql"
            )

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    def test(self):
        """Testa a conexão com o banco"""
        return self.conn.query("SELECT 1 AS ok;")
