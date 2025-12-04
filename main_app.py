# main_app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from db_manager import DBManager

# -------------------------------------------------
# 1. CARREGAR CONFIG.INICIAL (COOKIE / PREAUTHORIZED)
# -------------------------------------------------
try:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    if "credentials" not in config:
        config["credentials"] = {"usernames": {}}

except Exception as e:
    st.error("Erro ao carregar config.yaml. Certifique-se que o arquivo existe.")
    st.stop()

# -------------------------------------------------
# 2. INICIALIZAR DB E CARREGAR USUÁRIOS
# -------------------------------------------------
try:
    db = DBManager()
    users_from_db = db.get_users_for_auth()

    # Substitui completamente os usuários pela versão do BD
    config["credentials"]["usernames"] = users_from_db

except Exception as e:
    st.error(f"❌ Falha ao conectar ao banco. Erro: {e}")
    st.stop()


# -------------------------------------------------
# 3. INICIALIZAR STREAMLIT AUTHENTICATOR
# -------------------------------------------------
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config.get("preauthorized", {})
)


# -------------------------------------------------
# FORMULÁRIO DE CADASTRO
# -------------------------------------------------
def register_new_user_page():
    st.header("📝 Cadastro de Novo Jogador")

    if st.session_state["authentication_status"] is not None:
        st.warning("Você precisa deslogar para criar uma nova conta.")
        return

    with st.form("register_form"):
        username = st.text_input("Nome de Usuário (único)")
        name = st.text_input("Nome Completo")
        pwd1 = st.text_input("Senha", type="password")
        pwd2 = st.text_input("Repita a Senha", type="password")

        submitted = st.form_submit_button("Criar Conta")

    if submitted:
        if pwd1 != pwd2:
            st.error("As senhas não coincidem!")
            return

        if not username or not name or not pwd1:
            st.error("Preencha todos os campos.")
            return

        hashed = stauth.Hasher([pwd1]).generate()[0]

        if db.register_user(username, name, hashed):
            st.success("Conta criada com sucesso! Faça login na aba ao lado.")
        else:
            st.error("Erro ao cadastrar usuário. Talvez o username já exista.")


# -------------------------------------------------
# 4. APLICAÇÃO PRINCIPAL
# -------------------------------------------------
def run_app():

    st.title("🏆 AeroServ Bolão Mundial 2026")
    st.markdown("---")

    # Status de login
    if st.session_state["authentication_status"] is False:
        st.error("Usuário ou senha incorretos.")

    elif st.session_state["authentication_status"] is None:
        st.warning("Faça login ou crie uma conta para participar.")

    # -------------------------------------------------
    # ÁREA NÃO LOGADA: LOGIN / CADASTRO
    # -------------------------------------------------
    if st.session_state["authentication_status"] in (None, False):

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Cadastro"])

        with tab_login:
            try:
                authenticator.login("Login", "main")
            except Exception as e:
                st.error(f"Erro no login: {e}")

        with tab_register:
            register_new_user_page()

        return  # impede execução do resto antes de logar

    # -------------------------------------------------
    # ÁREA LOGADA
    # -------------------------------------------------
    username = st.session_state.get("username")
    user_details = config["credentials"]["usernames"].get(username, {})
    user_function = user_details.get("function", "Jogador")

    # Salva na sessão
    st.session_state["user_function"] = user_function

    # SIDEBAR
    st.sidebar.subheader(f"👋 Olá, {st.session_state.get('name')}")
    authenticator.logout("Sair", "sidebar")

    # -------------------------------------------------
    # SEÇÃO ADMIN
    # -------------------------------------------------
    if user_function == "Admin":
        st.header("🔧 Painel Administrativo")

        tab_add, tab_results = st.tabs(["➕ Cadastrar Jogo", "🏁 Resultados"])

        with tab_add:
            with st.form("game_form"):
                col1, col2 = st.columns(2)
                time_casa = col1.text_input("Time da Casa")
                time_fora = col2.text_input("Time Visitante")

                data_hora = st.text_input(
                    "Data e Hora (YYYY-MM-DD HH:MM:SS)",
                    "2026-06-10 16:00:00"
                )

                submit_game = st.form_submit_button("Salvar Jogo")

                if submit_game:
                    if db.add_game(time_casa, time_fora, data_hora):
                        st.success("Jogo cadastrado!")
                    else:
                        st.error("Erro ao salvar jogo. Confira a data/hora.")

        with tab_results:
            st.info("Em desenvolvimento.")

        st.markdown("---")

    # -------------------------------------------------
    # SEÇÃO PALPITES
    # -------------------------------------------------
    st.header("⚽ Registrar Palpites")
    open_games_df = db.get_open_games()

    if open_games_df.empty:
        st.warning("Nenhum jogo aberto no momento.")
    else:
        for idx, row in open_games_df.iterrows():
            with st.container():
                st.subheader(f"{row['time_casa']} x {row['time_fora']}")
                st.caption(f"Jogo {row['id']} • {row['data_hora']}")

                with st.form(f"form_{row['id']}"):
                    col1, col2 = st.columns(2)
                    pc = col1.number_input(
                        f"Gols {row['time_casa']}", min_value=0, key=f"pc{row['id']}"
                    )
                    pf = col2.number_input(
                        f"Gols {row['time_fora']}", min_value=0, key=f"pf{row['id']}"
                    )

                    save = st.form_submit_button("Salvar Palpite")

                if save:
                    user_id = db.get_user_id_by_username(username)
                    if db.save_palpite(user_id, row["id"], pc, pf):
                        st.success("Palpite salvo!")
                    else:
                        st.error("Erro ao salvar palpite.")

    st.markdown("---")
    st.subheader("🏅 Ranking")
    st.info("Ranking será exibido quando os jogos forem fechados.")


# -------------------------------------------------
# 5. EXECUTAR APP
# -------------------------------------------------
if __name__ == "__main__":
    try:
        authenticator.try_login()
    except:
        pass

    run_app()
