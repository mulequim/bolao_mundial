import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

from models.jogos import read_game_by_id
from models.palpites import salvar_palpite

def palpite_page():
    tz = pytz.timezone("America/Sao_Paulo")

    jogo_id = st.session_state.get("jogo_selecionado")
    if not jogo_id:
        st.warning("Nenhum jogo selecionado.")
        return

    jogo = read_game_by_id(jogo_id)
    if jogo is None:
        st.error("Jogo não encontrado.")
        return

    data_jogo = jogo["data_hora"]  # já vem convertido com timezone

    st.subheader("💬 Palpite")

    # Layout em duas colunas com bandeiras e nomes
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(f"assets/flags/{jogo['time_casa'].lower()}.png", width=80)  # bandeira do time da casa
        st.markdown(f"### {jogo['time_casa']}")
        placar_casa = st.number_input("Gols", min_value=0, step=1, key="placar_casa")
    with col2:
        st.image(f"assets/flags/{jogo['time_fora'].lower()}.png", width=80)  # bandeira do time de fora
        st.markdown(f"### {jogo['time_fora']}")
        placar_fora = st.number_input("Gols", min_value=0, step=1, key="placar_fora")

    st.caption(f"Grupo {jogo['grupo']} | {data_jogo.strftime('%d/%m/%Y %H:%M')}")

    # Verifica prazo
    limite = data_jogo - timedelta(minutes=45)
    agora = datetime.now(tz)

    if agora > limite:
        st.error("⏰ Palpites encerrados para este jogo.")
        return

    if st.button("Enviar Palpite"):
        salvar_palpite(st.session_state.user_id, jogo_id, placar_casa, placar_fora)
        st.success("Palpite registrado com sucesso!")
