# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:

    def __init__(self):
        try:
            # Conferindo se o secrets tem a chave correta
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError("Configuração 'connections.postgresql' não encontrada em st.secrets.")

            conf = st.secrets["connections"]["postgresql"]

            # Cria conexão usando EXACTAMENTE o formato que o Streamlit Cloud exige
            self.conn = st.connection(
                "postgresql",
                type="sql",
                dialect="postgresql",
                host=conf["host"],
                port=conf["port"],
                database=conf["database"],
                username=conf["username"],
                password=conf["password"],
            )

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    
    # -------------------------
    # FUNÇÃO DE TESTE (opcional)
    # -------------------------
    def test_connection(self):
        try:
            df = self.conn.query("SELECT 1 as ok;")
            return True
        except Exception as e:
            st.error(f"Erro no teste de conexão: {e}")
            return False
