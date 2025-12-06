import streamlit as st
from datetime import datetime, timedelta
from models.jogos import read_game_by_id
from models.palpites import salvar_palpite

def palpite_page():
    jogo_id = st.session_state.get("jogo_selecionado")
    if not jogo_id:
        st.warning("Nenhum jogo selecionado.")
        return

    jogo = read_game_by_id(jogo_id)
    if jogo is None:
        st.error("Jogo não encontrado.")
        return

    st.subheader("💬 Palpite")
    st.markdown(f"**{jogo['time_casa']} 🆚 {jogo['time_fora']}**")
    st.caption(f"Grupo {jogo['grupo']} | {jogo['data_hora'].strftime('%d/%m/%Y %H:%M')}")

    # Verifica prazo
    limite = jogo["data_hora"] - timedelta(minutes=45)
    if datetime.now() > limite:
        st.error("⏰ Palpites encerrados para este jogo.")
        return

    placar_casa = st.number_input(f"Gols de {jogo['time_casa']}", min_value=0, step=1)
    placar_fora = st.number_input(f"Gols de {jogo['time_fora']}", min_value=0, step=1)

    if st.button("Enviar Palpite"):
        salvar_palpite(jogo_id, st.session_state.user_id, placar_casa, placar_fora)
        st.success("Palpite registrado com sucesso!")
