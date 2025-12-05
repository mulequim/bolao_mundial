# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """
    Gerencia conexão SQL via st.connection e operações mínimas.
    Usa a configuração em st.secrets['connections']['postgresql'] (campo 'url').
    """

    def __init__(self):
        try:
            # Verifica se a configuração existe
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError("Configuração 'connections.postgresql' não encontrada em st.secrets. Verifique Settings > Secrets no Streamlit Cloud.")

            # Se você forneceu a URL em secrets (recomendado), apenas chame st.connection com o mesmo nome
            # O nome 'postgresql' deve bater com a chave em secrets (connections.postgresql)
            self.conn = st.connection("postgresql", type="sql")

        except Exception as e:
            # Mostra erro amigável e interrompe
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # método de teste simples
    def test_connection(self) -> bool:
        try:
            # Consulta curta e segura
            df = self.conn.query("SELECT 1 AS ok;")
            # se não lançou exceção, ok
            return True
        except Exception as e:
            st.error(f"Erro no teste de conexão: {e}")
            return False

    # Exemplos mínimos de uso (adicione os seus conforme necessário)
    def get_open_games(self) -> pd.DataFrame:
        try:
            return self.conn.query("SELECT id, time_casa, time_fora, data_hora FROM jogos WHERE status = 'Aberto' ORDER BY data_hora;")
        except Exception as e:
            st.error(f"Erro ao buscar jogos: {e}")
            return pd.DataFrame()

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        try:
            df = self.conn.query("SELECT id FROM usuarios WHERE username = %s;", params=(username,))
            if not df.empty:
                return int(df.iloc[0]["id"])
        except Exception as e:
            st.error(f"Erro ao buscar id do usuário: {e}")
        return None

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        try:
            self.conn.query(
                "INSERT INTO usuarios (username, name, password_hash) VALUES (%s, %s, %s);",
                params=(username, name, password_hash)
            )
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False
