# db_manager.py
import streamlit as st
import pandas as pd
# Removendo a tipagem List e Dict se não estiverem sendo usadas, para evitar erros de import
# from typing import List, Dict 
# Usando typing.Optional para compatibilidade
from typing import Optional 

class DBManager:
    """
    Classe responsável por todas as operações de banco de dados (USUARIOS, JOGOS, PALPITES).
    """
    
    def __init__(self):
        # --- DEBUG: PASSANDO CREDENCIAIS DIRETAMENTE PARA IGNORAR SECRETS.TOML ---
        self.conn = st.connection(
            "postgresql", 
            type="sql",
            dialect="postgresql",
            # ERRO ANTERIOR: server="swafxjmhzpoozhccsvzv.supabase.co", 
            
            # ✅ CORRIGIDO: USE 'host'
            host="swafxjmhzpoozhccsvzv.supabase.co", 
            
            database="postgres",
            username="postgres",
            password="_GJ$e5drTfRR6Yi", 
            port="5432" 
        )
        self.init_db()
        
    # --- MÉTODOS EXISTENTES ABAIXO (init_db, get_users_for_auth, etc.) ---
    
    # ... (init_db, get_users_for_auth, register_user, add_game, get_open_games, get_user_id_by_username, save_palpite) ...
