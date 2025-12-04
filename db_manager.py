# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional
import sys
import datetime

class DBManager:
    """
    Classe responsável por operações no banco de dados.
    Agora usa st.secrets["connections"]["postgresql"] (padrão Streamlit Cloud).
    """

    def __init__(self):
        try:
            # Usa a configuração que está em st.secrets['database']
            if "database" not in st.secrets:
                raise RuntimeError("Chave 'database' não encontrada em st.secrets. Verifique Settings > Secrets no Streamlit Cloud.")

            # Aguarda o Streamlit prover os secrets (em Cloud pode demorar um pouco)
            conf = st.secrets["database"]

            # Monta kwargs mínimos para st.connection
            conn_kwargs = {
                "dialect": "postgresql",
                "host": conf.get("host"),
                "database": conf.get("database"),
                "username": conf.get("user") or conf.get("username"),
                "password": conf.get("password"),
            }

            # porta
            port = conf.get("port")
            if port is not None:
                try:
                    conn_kwargs["port"] = int(port)
                except Exception:
                    conn_kwargs["port"] = port

            # sslmode opcional
            if "sslmode" in conf:
                conn_kwargs["sslmode"] = conf["sslmode"]

            # Cria a conexão (a string "postgresql" e type="sql" são importantes)
            self.conn = st.connection("postgresql", type="sql", **conn_kwargs)

            # Inicializa tabelas (se necessário)
            self.init_db()

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()

    # --- CRIA TABELAS ---
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

    # --- USUÁRIOS ---
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

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        try:
            df = self.conn.query(
