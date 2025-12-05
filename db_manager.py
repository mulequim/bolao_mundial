# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """
    Gerencia conexão SQL via st.connection e operações mínimas.
    Usa a configuração definida em [connections.postgresql] no secrets.toml.
    """

    def __init__(self):
        try:
            self.conn = st.connection("postgresql", type="sql")
            st.write("✅ Conexão inicializada com sucesso")
        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()


    def test_connection(self) -> bool:
        """Executa SELECT 1 para validar a conexão."""
        try:
            df = self.conn.query("SELECT 1 AS ok;", ttl=0)
            return not df.empty
        except Exception as e:
            st.error(f"Erro no teste de conexão: {e}")
            return False

    def get_open_games(self) -> pd.DataFrame:
        """Busca jogos abertos."""
        try:
            return self.conn.query(
                "SELECT id, time_casa, time_fora, data_hora "
                "FROM jogos WHERE status = 'Aberto' ORDER BY data_hora;"
            )
        except Exception as e:
            st.error(f"Erro ao buscar jogos: {e}")
            return pd.DataFrame()

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """Retorna o ID do usuário pelo username."""
        try:
            df = self.conn.query(
                "SELECT id FROM usuarios WHERE username = %s;",
                params=[(username,)]
            )
            if not df.empty:
                return int(df.iloc[0]["id"])
        except Exception as e:
            st.error(f"Erro ao buscar id do usuário: {e}")
        return None

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        """Registra novo usuário."""
        try:
            self.conn.query(
                "INSERT INTO usuarios (username, name, password_hash) VALUES (%s, %s, %s);",
                params=[(username, name, password_hash)]
            )
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False
