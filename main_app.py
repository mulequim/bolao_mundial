import streamlit as st
import db_manager as db  # importa o arquivo, não uma classe

st.title("🔌 Teste de Conexão com o Banco (Supabase)")

try:
    # tenta consultar qualquer tabela só para testar a conexão
    usuarios = db.get_usuarios()
    st.success("🎉 Teste concluído! Conexão funcionando.")
    st.dataframe(usuarios)

except Exception as e:
    st.error(f"❌ Erro ao conectar ao banco: {e}")
