import streamlit as st
import pandas as pd
from typing import Optional
import sys

class DBManager:
    """
    Classe responsável por todas as operações de banco de dados (USUARIOS, JOGOS, PALPITES, PONTUACAO).
    """

    def __init__(self):
        try:
            # Agora usa APENAS o secrets.toml do Streamlit Cloud
            self.conn = st.connection("postgresql", type="sql")

            self.init_db()

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            sys.exit(1)

    # --- INICIALIZAÇÃO ---

    def init_db(self):
        """Cria as tabelas se não existirem."""
        try:
            self.conn.query("""
                CREATE TABLE IF NOT EXISTS USUARIOS (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    function VARCHAR(20) DEFAULT 'Jogador',
                    email VARCHAR(100) UNIQUE
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS JOGOS (
                    id SERIAL PRIMARY KEY,
                    time_casa VARCHAR(100) NOT NULL,
                    time_fora VARCHAR(100) NOT NULL,
                    data_hora TIMESTAMP WITH TIME ZONE NOT NULL,
                    placar_casa_final INT,
                    placar_fora_final INT,
                    status VARCHAR(20) DEFAULT 'Aberto'
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS PALPITES (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    jogo_id INT NOT NULL,
                    palpite_casa INT NOT NULL,
                    palpite_fora INT NOT NULL,
                    UNIQUE (user_id, jogo_id),
                    FOREIGN KEY (user_id) REFERENCES USUARIOS(id) ON DELETE CASCADE,
                    FOREIGN KEY (jogo_id) REFERENCES JOGOS(id) ON DELETE CASCADE
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS PONTUACAO (
                    id SERIAL PRIMARY KEY,
                    user_id INT UNIQUE NOT NULL,
                    pontos_total INT DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES USUARIOS(id) ON DELETE CASCADE
                );
            """)

            st.success("Tabelas verificadas/criadas com sucesso!")

        except Exception as e:
            st.error(f"Erro ao inicializar o DB: {e}")

    # --- USUÁRIOS ---

    def get_users_for_auth(self) -> dict:
        """Retorna todos os usuários para autenticação."""
        df = self.conn.query("SELECT username, name, password_hash, function FROM USUARIOS;", ttl=600)

        users_dict = {}
        for _, row in df.iterrows():
            users_dict[row["username"]] = {
                "email": row["username"] + "@bolao.com.br",
                "name": row["name"],
                "password": row["password_hash"],
                "function": row["function"]
            }

        return users_dict

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        try:
            self.conn.query(
                """
                INSERT INTO USUARIOS (username, name, password_hash)
                VALUES (%s, %s, %s);
                """,
                params=(username, name, password_hash),
                ttl=0
            )
            return True

        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        df = self.conn.query(
            "SELECT id FROM USUARIOS WHERE username = %s;",
            params=(username,),
            ttl=600
        )
        if not df.empty:
            return df.iloc[0]["id"]
        return None

    # --- JOGOS ---

    def add_game(self, time_casa: str, time_fora: str, data_hora: str) -> bool:
        try:
            self.conn.query(
                """
                INSERT INTO JOGOS (time_casa, time_fora, data_hora, status)
                VALUES (%s, %s, %s, 'Aberto');
                """,
                params=(time_casa, time_fora, data_hora),
                ttl=0
            )
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar jogo: {e}")
            return False

    def get_open_games(self) -> pd.DataFrame:
        return self.conn.query(
            "SELECT id, time_casa, time_fora, data_hora FROM JOGOS WHERE status = 'Aberto' ORDER BY data_hora ASC;",
            ttl=60
        )

    # --- PALPITES ---

    def save_palpite(self, user_id: int, jogo_id: int, palpite_casa: int, palpite_fora: int) -> bool:
        try:
            self.conn.query(
                """
                INSERT INTO PALPITES (user_id, jogo_id, palpite_casa, palpite_fora)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, jogo_id) DO UPDATE
                SET palpite_casa = EXCLUDED.palpite_casa,
                    palpite_fora = EXCLUDED.palpite_fora;
                """,
                params=(user_id, jogo_id, palpite_casa, palpite_fora),
                ttl=0
            )
            return True

        except Exception as e:
            st.error(f"Erro ao salvar palpite: {e}")
            return False
