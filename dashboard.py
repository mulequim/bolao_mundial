import streamlit as st
import pandas as pd
from models.jogos import read_all_games

def dashboard_page():
    st.title("📅 Fase de Grupos - Copa do Mundo 2026")

    # Carrega todos os jogos
    jogos = read_all_games()

    # Converte data para string legível
    jogos["dia"] = jogos["data_hora"].dt.strftime("%d/%m/%Y")
    jogos = jogos.sort_values(by="data_hora")

    # Agrupa por dia
    dias = jogos["dia"].unique()
    for dia in dias:
        st.subheader(f"🗓 {dia}")
        jogos_dia = jogos[jogos["dia"] == dia]

        # Agrupa por grupo
        grupos = jogos_dia["grupo"].unique()
        for grupo in grupos:
            st.markdown(f"### Grupo {grupo}")
            jogos_grupo = jogos_dia[jogos_dia["grupo"] == grupo]

            for _, jogo in jogos_grupo.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1, 2, 1.5])
                with col1:
                    st.image(jogo["brasao_casa"], width=48)
                    st.markdown(f"**{jogo['time_casa']}**")
                with col2:
                    st.markdown("🆚")
                with col3:
                    st.image(jogo["brasao_fora"], width=48)
                    st.markdown(f"**{jogo['time_fora']}**")
                with col4:
                    st.markdown(f"⏰ {jogo['data_hora'].strftime('%H:%M')}")
                with col5:
                    st.markdown(f"📍 {jogo['local_jogo']}")
                st.markdown("---")
