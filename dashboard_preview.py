
import streamlit as st
import pandas as pd
from models.jogos import read_all_games

def dashboard_preview():
    st.subheader("🎉 A Copa está chegando!")
    st.markdown("Veja os jogos da fase de grupos e prepare seus palpites:")

    jogos = read_all_games()
    jogos["dia"] = jogos["data_hora"].dt.strftime("%d/%m/%Y")
    jogos = jogos.sort_values(by="data_hora")

    dias = jogos["dia"].unique()
    for dia in dias[:3]:  # mostra só os primeiros dias
        st.markdown(f"#### 🗓 {dia}")
        jogos_dia = jogos[jogos["dia"] == dia]
        grupos = jogos_dia["grupo"].unique()
        for grupo in grupos:
            st.markdown(f"**Grupo {grupo}**")
            jogos_grupo = jogos_dia[jogos_dia["grupo"] == grupo]
            for _, jogo in jogos_grupo.iterrows():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.image(jogo["brasao_casa"], width=48)
                    st.markdown(f"**{jogo['time_casa']}**")
                with col2:
                    st.markdown("🆚")
                with col3:
                    st.image(jogo["brasao_fora"], width=48)
                    st.markdown(f"**{jogo['time_fora']}**")
                st.markdown("---")

    st.markdown("### 🔐 Faça login para participar do bolão!")
    st.page_link("pages/register.py", label="📋 Cadastre-se agora", icon="📝")
