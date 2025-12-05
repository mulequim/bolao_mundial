import streamlit as st
from sqlalchemy import create_engine

class DBManager:
    def __init__(self):
        try:
            secrets = st.secrets["connections"]["postgresql"]
            url = (
                f"postgresql+psycopg2://{secrets['username']}:{secrets['password']}"
                f"@{secrets['host']}:{secrets['port']}/{secrets['database']}"
            )
            self.engine = create_engine(url, connect_args={"sslmode": "require"})
            st.write("✅ Conexão inicializada com sucesso (SQLAlchemy)")
        except Exception as e:
            st.error(f"❌ Falha crítica ao conectar ao banco: {e}")
            st.stop()
