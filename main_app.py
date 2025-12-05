import streamlit as st

# Cria a conexão usando o nome definido no secrets
conn = st.connection("postgresql", type="sql")

# Teste simples
def test_connection():
    try:
        result = conn.query("SELECT 1;", ttl=0)
        st.success("Conexão OK! Resultado: {}".format(result))
    except Exception as e:
        st.error(f"Erro na conexão: {e}")

test_connection()
