import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """Gerenciador de banco usando st.connection com Supabase PostgreSQL."""

    def __init__(self):
        try:
            # Agora usamos exatamente o formato do secrets testado
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError("Configuração 'connections.postgresql' não encontrada em st.secrets.")

            # Cria a conexão
            self.conn = st.connection("postgresql", type="sql")

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # -------------------------
    # USUÁRIOS
    # -------------------------
    def get_users_for_auth(self) -> dict:
        try:
            query = "SELECT username, name, password_hash, function FROM usuarios;"
            df = self.conn.query(query)
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return {}

        users = {}
        for _, row in df.iterrows():
            users[row["username"]] = {
                "email": f"{row['username']}@bolao.com",
                "name": row["name"],
                "password": row["password_hash"],
                "function": row["function"]
            }
        return users

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        try:
            sql = """
                INSERT INTO usuarios (username, name, password_hash)
                VALUES (%s, %s, %s);
            """
            self.conn.query(sql, params=(username, name, password_hash))
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        try:
            df = self.conn.query("SELECT id FROM usuarios WHERE username = %s;", params=(username,))
            if len(df) == 0:
                return None
            return int(df.iloc[0]["id"])
        except:
            return None

    # -------------------------
    # JOGOS
    # -------------------------
    def add_game(self, time_casa, time_fora, data_hora_str) -> bool:
        try:
            sql = """
                INSERT INTO jogos (time_casa, time_fora, data_hora)
                VALUES (%s, %s, %s);
            """
            self.conn.query(sql, params=(time_casa, time_fora, data_hora_str))
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar jogo: {e}")
            return False

    def get_open_games(self):
        try:
            return self.conn.query("SELECT * FROM jogos WHERE status = 'Aberto';")
        except Exception as e:
            st.error(f"Erro ao carregar jogos: {e}")
            return None

    # -------------------------
    # PALPITES
    # -------------------------
    def save_palpite(self, user_id, jogo_id, placar_casa, placar_fora):
        try:
            sql = """
                INSERT INTO palpites (user_id, jogo_id, palpite_casa, palpite_fora)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, jogo_id)
                DO UPDATE SET palpite_casa = EXCLUDED.palpite_casa,
                              palpite_fora = EXCLUDED.palpite_fora;
            """
            self.conn.query(sql, params=(user_id, jogo_id, placar_casa, placar_fora))
            return True
        except Exception as e:
            st.error(f"Erro ao salvar palpite: {e}")
            return False
