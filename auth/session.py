import streamlit as st

def init_session():
    """Inicializa variáveis de sessão."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None

def login_user(user_id: int, username: str):
    """Marca usuário como logado."""
    st.session_state.logged_in = True
    st.session_state.user_id = user_id
    st.session_state.username = username

def logout_user():
    """Finaliza sessão do usuário."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
