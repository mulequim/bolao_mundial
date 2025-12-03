# db_manager.py
import streamlit as st
import pandas as pd
from typing import List, Dict

class DBManager:
    """
    Classe responsável por todas as operações de banco de dados (USUARIOS, JOGOS, PALPITES).
    """
    
    def __init__(self):
        # GARANTA QUE ESTE NOME "postgresql" ESTÁ CORRETO
        self.conn = st.connection("postgresql", type="sql") 
        self.init_db()
    
    def init_db(self):
        """Cria as tabelas USUARIOS e PALPITES se elas não existirem."""
        try:
            # ... (SQL para criar USUARIOS e PALPITES) ...
            st.success("Tabelas verificadas/criadas com sucesso no banco de dados!")
        except Exception as e:
            # É aqui que a falha de conexão aparece!
            st.error(f"Erro ao inicializar o DB: {e}") 
            # Dica: Se você ver uma mensagem de erro aqui ao rodar, o problema é na conexão (secrets.toml)
