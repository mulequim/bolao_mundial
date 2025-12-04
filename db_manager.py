# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:
    """
    Classe responsável por operações no banco de dados.
    Agora usa st.secrets["connections"]["postgresql"] (padrão Streamlit Cloud).
    """

    def __init__(self):
        try:
            # Verifica se a chave correta existe
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError(
                    "Configuração ausente: st.secrets['connections']['postgresql'] não encontrada.\n"
                    "Corrija em Settings > Secrets no Streamlit Cloud."
                )

            # Lê configuração
            conf = st.secrets["connections"]["postgresql"]

            # Cria conexão
            self.conn = st.connection(
                "postgresql",
                type="sql",
                dialect="postgresql",
                host=conf["host"],
                port=conf.get("port", 5432),
                database=conf["database"],
                username=conf["username"],
                password=conf["password"],
                sslmode=conf.get("sslmode", "require")
            )

            # Inicializa tabelas
            self.init_db()

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # -------------------------------------------------------------------------
    # CRIA TABELAS
    # -------------------------------------------------------------------------
    def init_db(self):
        try:
            self.conn.query("""
                CREATE TABLE IF NOT EXISTS USUARIOS (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
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
                    user_id INT NOT NULL UNIQUE,
                    pontos_total INT DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES USUARIOS(id) ON DELETE CASCADE
                );
            """)

            st.success("Tabelas verificadas/criadas com sucesso!")

        except Exception as e:
            st.error(f"Erro ao criar tabelas: {e}")

    # -------------------------------------------------------------------------
    # BUSCAR USUÁRIOS (login)
    # -------------------------------------------------------------------------
    def get_users_for_auth(self) -> dict:
        try:
            df = self.conn.query(
                "SELECT username, name, password_hash, function FROM USUARIOS;",
                ttl=3600
            )
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return {}

        users = {}
        for _, row in df.iterrows():
            users[row['username']] = {
                'email': f"{row['username']}@bolao.com.br",
                'name': row['name'],
                'password': row['password_hash'],
                'function': row['function']
            }

        return users

    # -------------------------------------------------------------------------
    # REGISTRAR NOVO USUÁRIO
    # -------------------------------------------------------------------------
    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        try:
            self.conn.query("""
                INSERT INTO USUARIOS (username, name, password_hash)
                VALUES (%s, %s, %s);
            """, params=(username, name, password_hash))
            return True
        except Exception as e:
            st.error(f"Erro ao registrar usuário: {e}")
            return False

    # -------------------------------------------------------------------------
    # BUSCAR ID DO USUÁRIO
    # -------------------------------------------------------------------------
    def get_user_id_by_username(self, username: str) -> Optional[int]:
        try:
            df = self.conn.query(
                "SELECT id FROM USUARIOS WHERE username = %s;",
                params=(username,)
            )
            if len(df) == 0:
                return None
            return int(df.iloc[0]["id"])
        except Exception:
            return None
