import streamlit as st
import pandas as pd
from typing import Optional

class DBManager:

    def __init__(self):
        try:
            # Busca a configuração oficial
            if "connections" not in st.secrets or "postgresql" not in st.secrets["connections"]:
                raise RuntimeError("Configuração 'connections.postgresql' não encontrada em st.secrets.")

            conf = st.secrets["connections"]["postgresql"]

            # Conexão oficial
            self.conn = st.connection("postgresql", type="sql")

            # Cria tabelas se necessário
            self.init_db()

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # ---------------- Tabelas ----------------
    def init_db(self):
        try:
            self.conn.query("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    function VARCHAR(20) DEFAULT 'Jogador',
                    email VARCHAR(100)
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS jogos (
                    id SERIAL PRIMARY KEY,
                    time_casa VARCHAR(100),
                    time_fora VARCHAR(100),
                    data_hora TIMESTAMPTZ NOT NULL,
                    placar_casa_final INT,
                    placar_fora_final INT,
                    status VARCHAR(20) DEFAULT 'Aberto'
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS palpites (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    jogo_id INT NOT NULL,
                    palpite_casa INT NOT NULL,
                    palpite_fora INT NOT NULL,
                    UNIQUE(user_id, jogo_id)
                );
            """)

            self.conn.query("""
                CREATE TABLE IF NOT EXISTS pontuacao (
                    id SERIAL PRIMARY KEY,
                    user_id INT UNIQUE NOT NULL,
                    pontos_total INT DEFAULT 0
                );
            """)

        except Exception as e:
            st.error(f"Erro ao criar tabelas: {e}")

    # --------------- Usuários ----------------
    def get_users_for_auth(self) -> dict:
        try:
            df = self.conn.query("SELECT username, name, password_hash, function FROM usuarios;")
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
