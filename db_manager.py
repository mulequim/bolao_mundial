# db_manager.py
import streamlit as st
import pandas as pd
from typing import Optional 
import sys

class DBManager:
    """
    Classe responsável por todas as operações de banco de dados (USUARIOS, JOGOS, PALPITES).
    """
    
    def __init__(self):
        # As credenciais são passadas diretamente aqui para contornar o erro de leitura do secrets.toml 
        # em ambientes web/notebooks. Lembre-se de USAR 'host' em vez de 'server'.
        try:
            self.conn = st.connection(
                "postgresql", 
                type="sql",
                dialect="postgresql",
                host="swafxjmhzpoozhccsvzv.supabase.co", 
                database="postgres",
                username="postgres",
                password="_GJ$e5drTfRR6Yi", 
                port="5432"
                sslmode="require"
            )
            self.init_db()
        except Exception as e:
            # Em caso de falha de conexão, ele para o aplicativo e avisa.
            st.error(f"❌ Falha crítica ao conectar ao banco de dados. Verifique credenciais no db_manager.py. Erro: {e}")
            sys.exit(1)


    # --- INICIALIZAÇÃO E CRIAÇÃO DE TABELAS ---

    def init_db(self):
        """Cria as tabelas USUARIOS, JOGOS, PALPITES e PONTUACAO se elas não existirem."""
        try:
            # NOTA: Como as tabelas já foram criadas, estes comandos apenas garantem que elas existam
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
            # Este erro pode ocorrer se houver problemas de permissão, mesmo com a conexão aberta.
            st.error(f"Erro ao inicializar o DB (SQL): {e}")


    # --- OPERAÇÕES DE USUÁRIO (PARA AUTENTICAÇÃO E CADASTRO) ---

    def get_users_for_auth(self) -> dict:
        """
        Lê todos os usuários do DB para o módulo de autenticação.
        Retorna um dicionário no formato que o streamlit-authenticator espera.
        """
        query = "SELECT username, name, password_hash, function FROM USUARIOS;"
        df = self.conn.query(query, ttl=3600) # Cache por 1 hora

        users_dict = {}
        for index, row in df.iterrows():
            users_dict[row['username']] = {
                'email': row['username'] + '@bolao.com.br', 
                'name': row['name'],
                'password': row['password_hash'],
                'function': row['function']
            }
        
        return users_dict
    
    def register_user(self, username: str, name: str, password_hash: str) -> bool:
        """
        Insere um novo usuário (função 'Jogador') na tabela.
        """
        try:
            self.conn.query(
                f"INSERT INTO USUARIOS (username, name, password_hash) VALUES ('{username}', '{name}', '{password_hash}');",
                ttl=0
            )
            return True
        except Exception as e:
            # O erro mais comum aqui é 'duplicate key value' se o username já existir.
            st.error(f"Erro ao registrar o usuário: {e}")
            return False

    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """Busca o ID do usuário pelo nome de usuário."""
        query = f"SELECT id FROM USUARIOS WHERE username = '{username}';"
        df = self.conn.query(query, ttl=3600)
        
        if not df.empty:
            return df.iloc[0]['id']
        return None


    # --- OPERAÇÕES DE JOGO (ADMIN) ---

    def add_game(self, time_casa: str, time_fora: str, data_hora: str) -> bool:
        """
        Insere um novo jogo na tabela JOGOS.
        """
        try:
            self.conn.query(
                f"""
                INSERT INTO JOGOS (time_casa, time_fora, data_hora, status)
                VALUES ('{time_casa}', '{time_fora}', '{data_hora}', 'Aberto');
                """,
                ttl=0
            )
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar jogo: {e}")
            return False
            
    def get_open_games(self) -> pd.DataFrame:
        """Retorna todos os jogos com status 'Aberto'."""
        query = "SELECT id, time_casa, time_fora, data_hora FROM JOGOS WHERE status = 'Aberto' ORDER BY data_hora ASC;"
        return self.conn.query(query, ttl=60) # Cache por 60 segundos


    # --- OPERAÇÕES DE PALPITE (JOGADOR) ---

    def save_palpite(self, user_id: int, jogo_id: int, palpite_casa: int, palpite_fora: int) -> bool:
        """
        Salva ou atualiza o palpite do usuário para um jogo específico.
        """
        try:
            self.conn.query(
                f"""
                INSERT INTO PALPITES (user_id, jogo_id, palpite_casa, palpite_fora)
                VALUES ({user_id}, {jogo_id}, {palpite_casa}, {palpite_fora})
                ON CONFLICT (user_id, jogo_id) DO UPDATE
                SET palpite_casa = EXCLUDED.palpite_casa,
                    palpite_fora = EXCLUDED.palpite_fora;
                """,
                ttl=0
            )
            return True
        except Exception as e:
            st.error(f"Erro ao salvar palpite: {e}")
            return False
