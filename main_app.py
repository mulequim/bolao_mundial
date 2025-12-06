import streamlit as st
from auth.login import login_page
from auth.register import register_page
from auth.session import init_session
from pages.dashboard_preview import dashboard_preview

st.set_page_config(page_title="Bolão Copa 2026", layout="wide")
st.title("🏆 Bolão Copa do Mundo 2026")

# Inicializa sessão
init_session()

# Garante que o estado do menu existe
if "menu" not in st.session_state:
    st.session_state["menu"] = "Início"

# Sidebar com menu
def get_menu():
    # Lista de opções válidas
    menu_options = ["Início", "Login", "Cadastro", "Dashboard", "Palpite", "Logout"]

    # Pega o valor atual do session_state, ou usa "Início" como padrão
    current_menu = st.session_state.get("menu", "Início")

    # Se o valor não estiver na lista, volta para "Início"
    if current_menu not in menu_options:
        current_menu = "Início"

    return current_menu, menu_options

# 🔧 Cria o selectbox do menu
menu_default, menu_options = get_menu()
menu = st.sidebar.selectbox(
    "Menu",
    menu_options,
    index=menu_options.index(menu_default)
)

# Renderização das páginas
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

elif menu == "Palpite":
    from pages.palpite import palpite_page
    palpite_page()

elif menu == "Logout":
    # Reseta sessão e volta para Início
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state["menu"] = "Início"
    st.success("Você saiu da sua conta com sucesso!")
    st.rerun()

else:
    # Página inicial (preview dos jogos + chamada para login/cadastro)
    st.subheader("⚽ Fase de Grupos - Copa 2026")
    dashboard_preview()

    st.markdown("---")
    st.info("🔐 Para participar do bolão, faça seu cadastro ou login!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Login"):
            st.session_state["menu"] = "Login"
            st.rerun()
    with col2:
        if st.button("📝 Cadastro"):
            st.session_state["menu"] = "Cadastro"
            st.rerun()
