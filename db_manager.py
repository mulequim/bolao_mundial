# db_manager.py (VERSÃO SIMPLIFICADA)
import streamlit as st
import pandas as pd
# Importe as outras dependências necessárias

class DBManager:
    def __init__(self):
        try:
            # O Streamlit Cloud LÊ O secrets.toml AUTOMATICAMENTE!
            self.conn = st.connection(
                "postgresql", # Nome da conexão no secrets.toml
                type="sql"
            )
            # Chama a função que cria/verifica as tabelas
            self.init_db() 
        except Exception as e:
            st.error(f"❌ Falha ao inicializar a conexão no Cloud: {e}")
            st.stop()
            
    # O restante dos seus métodos (init_db, get_users_for_auth, etc.) deve vir aqui
    
    # ... (init_db, get_users_for_auth, register_user, add_game, etc.) ...
