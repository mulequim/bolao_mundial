# main_app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from db_manager import DBManager # Módulo de conexão com o Supabase

# --- 1. CONFIGURAÇÃO INICIAL E CARREGAMENTO DE DADOS ---

# Carrega a configuração do cookie e de usuários do arquivo config.yaml
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Erro: Arquivo 'config.yaml' não encontrado. Verifique a estrutura do projeto.")
    st.stop()

# Inicializa o gerenciador de banco de dados e cria as tabelas (se não existirem)
# Nota: As tabelas já foram criadas manualmente, mas isso garante o objeto 'db'
try:
    db = DBManager()
    
    # Carrega os usuários do DB para o módulo de autenticação
    users_from_db = db.get_users_for_auth()
    
    # Atualiza a configuração de credenciais com os usuários do DB
    config['credentials']['usernames'].update(users_from_db)
    
except Exception as e:
    # Se o DBManager falhar (geralmente por causa do secrets.toml), o app para aqui
    st.error(f"❌ Falha crítica ao conectar ao banco de dados. Verifique secrets.toml. Erro: {e}")
    st.stop()


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# --- 2. FUNÇÃO DE CADASTRO DE NOVO USUÁRIO (JOGADOR) ---

def register_new_user_page():
    """Formulário para cadastro de novos usuários (Jogadores)."""
    st.header("👤 Novo Cadastro de Jogador")

    if st.session_state["authentication_status"] is None:
        
        with st.form("register_form"):
            username = st.text_input("Nome de Usuário (único)")
            name = st.text_input("Nome Completo")
            new_password = st.text_input("Senha", type='password')
            repeat_password = st.text_input("Repita a Senha", type='password')
            
            submitted = st.form_submit_button("Criar Conta")

        if submitted:
            if new_password != repeat_password:
                st.error("As senhas não coincidem!")
            elif not username or not name or not new_password:
                st.error("Por favor, preencha todos os campos.")
            else:
                # 1. Gerar o hash da senha
                hashed_password = stauth.Hasher([new_password]).generate()[0]
                
                # 2. Registrar no DB (a função padrão é 'Jogador')
                if db.register_user(username, name, hashed_password):
                    st.success("Cadastro realizado com sucesso! Faça login na aba ao lado.")
                    st.session_state["authentication_status"] = None
                else:
                    st.error("Erro ao tentar cadastrar. Nome de usuário já existe ou falha no DB.")
    else:
        st.warning("Você precisa sair da sua conta para criar um novo usuário.")
        authenticator.logout('Sair', 'main')


# --- 3. HOME PAGE E ROTEAMENTO (RUN_APP) ---

def run_app():
    st.set_page_config(page_title="AeroServ Bolão de Palpites", layout="wide")
    
    st.title("🏆 AeroServ Bolão Mundial 2026")
    st.markdown("---")
    
    # Verifica o status de login
    if st.session_state["authentication_status"] is False:
        st.error('Nome de usuário/senha incorretos.')
    elif st.session_state["authentication_status"] is None:
        st.warning('Por favor, faça login ou cadastre-se para participar.')

    # LÓGICA DE LOGIN / CADASTRO (Não Logado)
    if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False:
        
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Cadastro"])
        
        with tab_login:
            try:
                authenticator.login('Login', 'main')
            except Exception as e:
                st.error(e)

        with tab_register:
            register_new_user_page()
            
    # LÓGICA DO APP (Usuário Logado)
    elif st.session_state["authentication_status"]:
        
        # Exibe o nome do usuário e o botão de logout
        st.sidebar.subheader(f"👋 Olá, {st.session_state['name']}!")
        authenticator.logout('Sair', 'sidebar')

        user_function = st.session_state['user_function']
        
        # --- SEÇÃO ADMINISTRATIVA (Apenas para Admin) ---
        if user_function == 'Admin':
            st.header("🔑 Painel do Administrador")
            tab_add_game, tab_manage_results = st.tabs(["➕ Cadastrar Jogo", "✅ Inserir Resultados"])
            
            with tab_add_game:
                st.markdown("##### 🏟️ Registrar Nova Partida")
                with st.form("game_form"):
                    col1, col2 = st.columns(2)
                    time_casa = col1.text_input("Time da Casa")
                    time_fora = col2.text_input("Time Visitante")
                    
                    # O formato de data/hora deve ser 'YYYY-MM-
