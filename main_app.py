# main_app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from db_manager import DBManager  # Módulo de conexão com o Supabase

# --- 1. CONFIGURAÇÃO INICIAL E CARREGAMENTO DE DADOS ---

# Carrega a configuração do cookie e de usuários do arquivo config.yaml
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Erro: Arquivo 'config.yaml' não encontrado. Verifique a estrutura do projeto.")
    st.stop()

# Garante que a chave 'credentials' e 'usernames' existam no config (evita KeyError)
if 'credentials' not in config:
    config['credentials'] = {}
if 'usernames' not in config['credentials']:
    config['credentials']['usernames'] = {}

# Inicializa o gerenciador de banco de dados e cria as tabelas (se não existirem)
try:
    db = DBManager()

    # Carrega os usuários do DB para o módulo de autenticação
    users_from_db = db.get_users_for_auth() or {}

    # Atualiza a configuração de credenciais com os usuários do DB
    # users_from_db possui a forma { username: {email, name, password, function} }
    config['credentials']['usernames'].update(users_from_db)

except Exception as e:
    st.error(f"❌ Falha crítica ao conectar ao banco de dados. Verifique st.secrets no Streamlit Cloud. Erro: {e}")
    st.stop()


# Cria o objeto authenticator com segurança (tratando chaves ausentes)
auth_args = (
    config.get('credentials', {}),
    config.get('cookie', {}).get('name', 'bolao_cookie'),
    config.get('cookie', {}).get('key', 'some_random_key_should_be_here'),
    config.get('cookie', {}).get('expiry_days', 30),
    config.get('preauthorized', {})
)

authenticator = stauth.Authenticate(*auth_args)


# inicializa variáveis de sessão que serão usadas
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_function' not in st.session_state:
    st.session_state['user_function'] = None


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
                    # garante que o fluxo de login continue limpo
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

    # Mostra estado de autenticação
    if st.session_state["authentication_status"] is False:
        st.error('Nome de usuário/senha incorretos.')
    elif st.session_state["authentication_status"] is None:
        st.warning('Por favor, faça login ou cadastre-se para participar.')

    # LÓGICA DE LOGIN / CADASTRO (Não Logado)
    if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False:

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Cadastro"])

        with tab_login:
            try:
                name, auth_status, username = authenticator.login('Login', 'main')
                # guarda no estado de sessão (a lib já faz isso, mas guardamos para consistência)
                st.session_state['name'] = name
                st.session_state['authentication_status'] = auth_status
                st.session_state['username'] = username
            except Exception as e:
                st.error(f"Erro no login: {e}")

        with tab_register:
            register_new_user_page()

    # LÓGICA DO APP (Usuário Logado)
    elif st.session_state["authentication_status"]:

        # Pega função do usuário logado a partir do config atualizado (se existir)
        username = st.session_state.get('username')
        user_function = None
        if username and username in config.get('credentials', {}).get('usernames', {}):
            user_function = config['credentials']['usernames'][username].get('function', 'Jogador')

        st.session_state['user_function'] = user_function or 'Jogador'

        # Exibe o nome do usuário e o botão de logout
        st.sidebar.subheader(f"👋 Olá, {st.session_state.get('name', 'Usuário')}!")
        authenticator.logout('Sair', 'sidebar')

        # --- SEÇÃO ADMINISTRATIVA (Apenas para Admin) ---
        if st.session_state['user_function'] == 'Admin':
            st.header("🔑 Painel do Administrador")
            tab_add_game, tab_manage_results = st.tabs(["➕ Cadastrar Jogo", "✅ Inserir Resultados"])

            with tab_add_game:
                st.markdown("##### 🏟️ Registrar Nova Partida")
                with st.form("game_form"):
                    col1, col2 = st.columns(2)
                    time_casa = col1.text_input("Time da Casa")
                    time_fora = col2.text_input("Time Visitante")

                    # O formato de data/hora deve ser 'YYYY-MM-DD HH:MM:SS'
                    data_hora_str = st.text_input("Data e Hora (AAAA-MM-DD HH:MM:SS)", value="2026-06-12 17:00:00")

                    submitted = st.form_submit_button("Salvar Jogo")

                    if submitted:
                        if db.add_game(time_casa, time_fora, data_hora_str):
                            st.success(f"Jogo {time_casa} x {time_fora} cadastrado com sucesso!")
                        else:
                            st.error("Falha ao cadastrar jogo. Verifique o formato da data.")

            with tab_manage_results:
                st.warning("Funcionalidade em desenvolvimento: Fechamento de jogos e cálculo de pontuação.")

            st.markdown("---")

        # --- SEÇÃO PRINCIPAL (Para Todos Logados) ---
        st.header("⚽ Registrar Palpites")
        st.info("Aqui você verá os jogos abertos e o ranking atualizado.")

        open_games_df = db.get_open_games()

        if open_games_df is None or open_games_df.empty:
            st.warning("Nenhuma partida disponível para palpite no momento. Aguarde o Admin cadastrar novos jogos.")
        else:
            st.markdown("##### Partidas em Aberto:")

            for _, row in open_games_df.iterrows():
                with st.container():
                    st.markdown(f"**{row['time_casa']}** vs **{row['time_fora']}**")
                    st.caption(f"ID do Jogo: {row['id']} | Data: {row['data_hora']}")

                    with st.form(f"palpite_form_{row['id']}"):
                        col1, col2 = st.columns(2)

                        palpite_casa = col1.number_input(f"Placar {row['time_casa']}", min_value=0, step=1, key=f"pc_{row['id']}")
                        palpite_fora = col2.number_input(f"Placar {row['time_fora']}", min_value=0, step=1, key=f"pf_{row['id']}")

                        submitted_palpite = st.form_submit_button("Salvar Meu Palpite")

                        if submitted_palpite:
                            # Pega user_id pelo username atual
                            user_id = db.get_user_id_by_username(st.session_state.get('username'))
                            if user_id is None:
                                st.error("Erro: não foi possível identificar seu ID de usuário.")
                            else:
                                ok = db.save_palpite(user_id, int(row['id']), int(palpite_casa), int(palpite_fora))
                                if ok:
                                    st.success(f"Palpite para o jogo {row['id']} salvo com sucesso.")
                                else:
                                    st.error("Falha ao salvar palpite.")

        st.markdown("---")
        st.subheader("🔥 Ranking Atual")
        st.info("Tabela de Ranking será exibida aqui após o Admin fechar as partidas.")


# --- 4. EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    # Ao executar diretamente, tenta login via cookie/sessão
    try:
        name, authentication_status, username = authenticator.try_login()
        st.session_state['name'] = name
        st.session_state['authentication_status'] = authentication_status
        st.session_state['username'] = username

        # Se autenticado, define função do usuário para usar no layout
        if authentication_status:
            if username and username in config.get('credentials', {}).get('usernames', {}):
                st.session_state['user_function'] = config['credentials']['usernames'][username].get('function', 'Jogador')

    except Exception:
        # Não fatal — prossegue para run_app que tratará estado None/False
        pass

    run_app()
