# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """Gerencia conexão e queries ao PostgreSQL via st.connection."""

    def __init__(self):
        try:
            # Conecta usando o bloco [connections.postgresql] do secrets TOML
            self.conn = st.connection("postgresql", type="sql")
        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # --- TESTE SIMPLES ---
    def test_connection(self):
        try:
            df = self.conn.query("SELECT 1 AS ok;")
            return True
        except Exception:
            return False

    # --- BUSCAR USUÁRIOS (para login) ---
    def get_users_for_auth(self) -> dict:
        try:
            df = self.conn.query("SELECT username, name, password_hash, function FROM usuarios;")
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return {}

        users = {}
        for _, r in df.iterrows():
            users[r["username"]] = {
                "email": f"{r['username']}@bolao.com",
                "name": r["name"],
                "password": r["password_hash"],
                "function": r["function"],
            }

        return users
