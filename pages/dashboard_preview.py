import streamlit as st
import pandas as pd
from models.jogos import read_all_games
from utils.jogo_card import exibir_jogo  # Certifique-se de que essa função está em utils/jogo_card.py

def dashboard_preview():
    st.subheader("🎉 A Copa está chegando!")
    st.markdown("Veja os jogos da fase de grupos e prepare seus palpites:")

    jogos = read_all_games()
    if jogos.empty:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    # Converte data para string legível
    jogos["dia"] = pd.to_datetime(jogos["data_hora"]).dt.strftime("%d/%m/%Y")
    jogos = jogos.sort_values(by="data_hora")

    # Agrupa por dia
    dias = jogos["dia"].unique()
    for dia in dias[:3]:  # mostra só os primeiros dias para criar expectativa
        st.markdown(f"### 🗓 {dia}")
        jogos_dia = jogos[jogos["dia"] == dia]

        # Agrupa por grupo
        grupos = jogos_dia["grupo"].unique()
        for grupo in grupos:
            st.markdown(f"#### 🧩 Grupo {grupo}")
            jogos_grupo = jogos_dia[jogos_dia["grupo"] == grupo]
            for _, jogo in jogos_grupo.iterrows():
                exibir_jogo(jogo)  # visualização com bandeiras e botão "Palpite"

    st.markdown("### 🔐 Faça login para participar do bolão!")
    st.info("Cadastre-se ou faça login para enviar seus palpites e entrar no ranking.")
