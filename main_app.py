import streamlit as st
from auth.login import login_page
from auth.register import register_page
from auth.session import init_session
from pages.dashboard_preview import dashboard_preview

st.set_page_config(page_title="Bolão Copa 2026", layout="wide")
st.title("🏆 Bolão Copa do Mundo 2026")
init_session()

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Início", "Login", "Cadastro", "Dashboard"])

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
else:
    # Página inicial (preview dos jogos + chamada para login/cadastro)
    st.subheader("⚽ Fase de Grupos - Copa 2026")
    dashboard_preview()

    st.markdown("---")
    st.info("🔐 Para participar do bolão, faça seu cadastro ou login!")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("main_app.py", label="➡️ Login", icon="🔑")
    with col2:
        st.page_link("main_app.py", label="📝 Cadastro", icon="📋")
