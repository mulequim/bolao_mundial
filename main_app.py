import streamlit as st
from auth.login import login_page
from auth.register import register_page
from auth.session import init_session

st.title("Bolão Copa do Mundo 2026")
init_session()

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Dashboard"])

if menu == "Login":
    login_page()
elif menu == "Cadastro":
    register_page()
elif menu == "Dashboard":
    if st.session_state.logged_in:
        st.success(f"Bem-vindo, {st.session_state.username}!")
        st.write("Aqui vai o painel principal do bolão.")
    else:
        st.warning("Faça login para acessar o dashboard.")
