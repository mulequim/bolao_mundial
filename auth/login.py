import streamlit as st
from auth.session import init_session, login_user, logout_user
from models.usuarios import read_users
from utils.auth import verify_password
from pages.dashboard_preview import dashboard_preview

def login_page():
    init_session()
    st.title("🏆 Bolão Copa do Mundo 2026")

    if st.session_state.logged_in:
        st.success(f"Você está logado como {st.session_state.username}")
        if st.button("Ir para o Dashboard"):
            st.switch_page("pages/dashboard.py")
        if st.button("Logout"):
            logout_user()
            st.info("Sessão encerrada.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                users = read_users()
                user = users[users["username"] == username]
                if not user.empty and verify_password(password, user.iloc[0]["password_hash"]):
                    login_user(user.iloc[0]["id"], username)
                    st.success("Login realizado com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        with col2:
            st.markdown("### Ainda não tem conta?")
            if st.button("📋 Cadastre-se aqui"):
                st.session_state["menu"] = "Cadastro"
                st.rerun()

        st.markdown("---")
        dashboard_preview()
