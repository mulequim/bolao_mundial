# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional
import sys
import datetime

class DBManager:
    """
    Classe responsável por todas as operações de banco de dados (USUARIOS, JOGOS, PALPITES).
    Lê as credenciais de st.secrets['database'] e cria uma conexão via st.connection(..., type='sql').
    """

    def __init__(self):
        try:
            # Busca as credenciais no Streamlit Secrets (compatível com Streamlit Cloud)
            if "database" not in st.secrets:
                raise RuntimeError("Chave 'database' não encontrada em st.secrets. Verifique Settings > Secrets no Streamlit Cloud.")

            conf = st.secrets["database"]

            # Monta kwargs para st.connection
            conn_kwargs = {
                "dialect": "postgresql",
                "host": conf.get("host"),
                "database": conf.get("database"),
                "username": conf.get("user") or conf.get("username"),
                "password": conf.get("password"),
            }

            # Porta pode ser número ou string no secrets, certifique-se que seja int
            port = conf.get("port")
            if port is not None:
                try:
                    conn_kwargs["port"] = int(port)
                except Exception:
                    conn_kwargs["port"] = port  # deixa como está, st.connection pode aceitar string

            # sslmode se fornecido
            if "sslmode" in conf:
                conn_kwargs["sslmode"] = conf["sslmode"]

            # Cria a conexão SQL com os kwargs explicitamente (evita Missing SQL DB connection configuration)
            self.conn = st.connection("postgresql", type="sql", **conn_kwargs)

            # Teste simples de conexão (não obrigatório, ajuda a debugar)
            try:
                _ = self.conn.query("SELECT 1;")
            except Exception as e:
                raise RuntimeError(f"Falha ao testar a conexão SQL logo após st.connection(): {e}")

            # Inicializa tabelas (se necessário)
            self.init_db()

        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            # Para evitar deixar o app em estado indefinido, paramos a execução
            sys.exit(1)


    # --- INICIALIZAÇÃO E CRIAÇÃO DE TABELAS ---
    def init_db(self):
        """Cria as tabelas USUARIOS, JOGOS, PALPITES e PONTUACAO se elas não existirem."""
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
            st.success("Tabelas verificadas/criadas com sucesso no banco de dados!")
        except Exception as e:
            st.error(f"Erro ao inicializar o DB (SQL): {e}")


    # --- OPERAÇÕES DE USUÁRIO (PARA AUTENTICAÇÃO E CADASTRO) ---
    def get_users_for_auth(self) -> dict:
        """
        Lê todos os usuários do DB para o módulo de autenticação.
        Retorna um dicionário no formato que o streamlit-authenticator espera.
        """
        try:
            query = "SELECT username, name, password_hash, function FROM USUARIOS;"
            df = self.conn.query(query, ttl=3600)  # Cache por 1 hora
        except Exception as e:
            st.error(f"Erro ao buscar usuários do DB: {e}")
            return {}

        users_dict = {}
        for _, row in df.iterrows():
            users_dict[row['username']] = {
                'email': (row['username'] + '@bolao.com.br') if pd.notna(row['username']) else '',
                'name': row['name'] if pd.notna(row['name']) else '',
                'password': row['password_hash'] if pd.notna(row['password_hash']) else '',
                'function': row['function'] if pd.notna(row['function']) else 'Jogador'
            }

        return users_dict

    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        """
        Insere um novo usuário (função 'Jogador') na tabela.
        """
        try:
            # Usa params para evitar SQL injection
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
            st.error(f"Erro ao registrar o usuário: {e}")
            return False

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """Busca o ID do usuário pelo nome de usuário."""
        try:
            query = "SELECT id FROM USUARIOS WHERE username = %s;"
            df = self.conn.query(query, params=(username,), ttl=3600)
            if not df.empty:
                return int(df.iloc[0]['id'])
        except Exception as e:
            st.error(f"Erro ao buscar id do usuário: {e}")
        return None


    # --- OPERAÇÕES DE JOGO (ADMIN) ---
    def add_game(self, time_casa: str, time_fora: str, data_hora: str) -> bool:
        """
        Insere um novo jogo na tabela JOGOS.
        Espera data_hora em string no formato ISO ou 'YYYY-MM-DD HH:MM:SS'
        """
        try:
            # Tenta converter para timestamp para verificar formato (opcional)
            # Não é estritamente necessário, mas ajuda a detectar erros no momento do input
            try:
                # aceita ISO ou formato comum
                datetime.datetime.fromisoformat(data_hora)
            except Exception:
                # tenta com format padrão
                try:
                    datetime.datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    # não conseguiu parsear - ainda assim deixa passar e o Postgres tentará converter
                    pass

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
        """Retorna todos os jogos com status 'Aberto'."""
        try:
            query = "SELECT id, time_casa, time_fora, data_hora FROM JOGOS WHERE status = 'Aberto' ORDER BY data_hora ASC;"
            return self.conn.query(query, ttl=60)  # Cache por 60 segundos
        except Exception as e:
            st.error(f"Erro ao buscar jogos abertos: {e}")
            return pd.DataFrame()


    # --- OPERAÇÕES DE PALPITE (JOGADOR) ---
    def save_palpite(self, user_id: int, jogo_id: int, palpite_casa: int, palpite_fora: int) -> bool:
        """
        Salva ou atualiza o palpite do usuário para um jogo específico.
        """
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
