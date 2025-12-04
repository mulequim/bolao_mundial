import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """
    Conecta ao banco usando apenas st.connection('postgresql').
    O Streamlit pega automaticamente tudo do secrets TOML.
    """

    def __init__(self):
        try:
            # Conecta conforme definido em secrets.toml ( connections.postgresql )
            self.conn = st.connection("postgresql", type="sql")
        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # ------------------- USUÁRIOS -------------------

    def get_users_for_auth(self) -> dict:
        try:
            df = self.conn.query("SELECT username, name, password_hash, function FROM usuarios;")
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return {}

        users = {}
        for _, row in df.iterrows():
            users[row["username"]] = {
                "email": f"{row['username']}@bolao.com.br",
                "name": row["name"],
                "password": row["password_hash"],
                "function": row["function"]
            }
        return users

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        try:
            df = self.conn.query(
                "SELECT id FROM usuarios WHERE username=%s LIMIT 1;",
                params=(username,)
            )
            if df.empty:
                return None
            return int(df.iloc[0]["id"])
        except Exception as e:
            st.error(f"Erro ao buscar user_id: {e}")
            return None

    def register_user(self, username, name, password_hash):
        try:
            self.conn.query("""
                INSERT INTO usuarios (username, name, password_hash)
                VALUES (%s, %s, %s)
            """, params=(username, name, password_hash))
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False

    # ------------------- JOGOS -------------------

    def get_open_games(self):
        try:
            return self.conn.query("SELECT * FROM jogos WHERE status='Aberto';")
        except Exception as e:
            st.error(f"Erro ao buscar jogos: {e}")
            return pd.DataFrame()

    def add_game(self, time_casa, time_fora, data_hora):
        try:
            self.conn.query("""
                INSERT INTO jogos (time_casa, time_fora, data_hora)
                VALUES (%s, %s, %s)
            """, params=(time_casa, time_fora, data_hora))
            return True
        except Exception as e:
            st.error(f"Erro ao cadastrar jogo: {e}")
            return False

    # ------------------- PALPITES -------------------

    def save_palpite(self, user_id, jogo_id, palpite_casa, palpite_fora):
        try:
            self.conn.query("""
                INSERT INTO palpites (user_id, jogo_id, palpite_casa, palpite_fora)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, jogo_id)
                DO UPDATE SET palpite_casa=EXCLUDED.palpite_casa, palpite_fora=EXCLUDED.palpite_fora
            """, params=(user_id, jogo_id, palpite_casa, palpite_fora))
            return True
        except Exception as e:
            st.error(f"Erro ao salvar palpite: {e}")
            return False
