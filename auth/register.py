import streamlit as st
from models.usuarios import read_users, create_user
from utils.auth import hash_password

def register_page():
    st.subheader("Cadastro de Usuário")

    username = st.text_input("Usuário")
    name = st.text_input("Nome completo")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    function = "player"  # padrão para novos usuários

    if st.button("Cadastrar"):
        if username and name and email and password:
            # Carrega todos os usuários
            users = read_users()

            # Verifica duplicidade
            if username in users["username"].values:
                st.error("Esse nome de usuário já está em uso.")
            elif email in users["email"].values:
                st.error("Esse email já está cadastrado.")
            else:
                password_hash = hash_password(password)
                ok = create_user(username, name, password_hash, function, email)
                if ok:
                    st.success("Usuário cadastrado com sucesso!")
                    st.session_state["menu"] = "Login"
                    st.rerun()
                else:
                    st.error("Erro ao cadastrar usuário.")
        else:
            st.warning("Preencha todos os campos.")
