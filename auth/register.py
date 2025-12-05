import streamlit as st
from utils.auth import hash_password
from models.usuarios import create_user

def register_page():
    st.subheader("Cadastro de Usuário")

    username = st.text_input("Usuário")
    name = st.text_input("Nome completo")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    function = "player"  # padrão para novos usuários

    if st.button("Cadastrar"):
        if username and name and email and password:
            password_hash = hash_password(password)
            ok = create_user(username, name, password_hash, function, email)
            if ok:
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar usuário.")
        else:
            st.warning("Preencha todos os campos.")
