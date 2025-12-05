import streamlit as st
from utils.auth import verify_password
from models.usuarios import read_users
from auth.session import login_user, logout_user, init_session

def login_page():
    init_session()
    st.subheader("Login")

    if st.session_state.logged_in:
        st.success(f"Você está logado como {st.session_state.username}")
        if st.button("Logout"):
            logout_user()
            st.info("Sessão encerrada.")
    else:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            users = read_users()
            user = users[users["username"] == username]
            if not user.empty:
                stored_hash = user.iloc[0]["password_hash"]
                if verify_password(password, stored_hash):
                    login_user(user.iloc[0]["id"], username)
                    st.success("Login realizado com sucesso!")
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado.")
