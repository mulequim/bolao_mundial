# db_manager.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional

class DBManager:
    """
    Gerencia conexão SQL via SQLAlchemy.
    Usa as credenciais definidas em [connections.postgresql] no secrets.toml.
    """

    def __init__(self):
        try:
            # Monta a URL de conexão a partir dos secrets
            secrets = st.secrets["connections"]["postgresql"]
            user = secrets["username"]
            password = secrets["password"]
            host = secrets["host"]
            port = secrets["port"]
            database = secrets["database"]

            url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

            # Cria engine com SSL
            self.engine = create_engine(url, connect_args={"sslmode": "require"})
            st.write("✅ Conexão inicializada com sucesso (SQLAlchemy)")
        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    def test_connection(self) -> bool:
        """Executa SELECT 1 para validar a conexão."""
        try:
            df = pd.read_sql("SELECT 1 AS ok;", self.engine)
            st.write("Resultado:", df)
            return not df.empty
        except Exception as e:
            st.error(f"Erro no teste de conexão: {e}")
            return False

    def get_open_games(self) -> pd.DataFrame:
        """Busca jogos abertos."""
        try:
            query = text("SELECT id, time_casa, time_fora, data_hora "
                         "FROM jogos WHERE status = 'Aberto' ORDER BY data_hora;")
            return pd.read_sql(query, self.engine)
        except Exception as e:
            st.error(f"Erro ao buscar jogos: {e}")
            return pd.DataFrame()

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """Retorna o ID do usuário pelo username."""
        try:
            query = text("SELECT id FROM usuarios WHERE username = :username;")
            df = pd.read_sql(query, self.engine, params={"username": username})
            if not df.empty:
                return int(df.iloc[0]["id"])
        except Exception as e:
            st.error(f"Erro ao buscar id do usuário: {e}")
        return None

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        """Registra novo usuário."""
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO usuarios (username, name, password_hash) "
                         "VALUES (:username, :name, :password_hash);"),
                    {"username": username, "name": name, "password_hash": password_hash}
                )
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False
