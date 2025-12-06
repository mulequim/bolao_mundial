import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def exibir_jogo(jogo):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.image(jogo["brasao_casa"], width=48)
        st.markdown(f"**{jogo['time_casa']}**")
    with col2:
        st.markdown("🆚")
    with col3:
        st.image(jogo["brasao_fora"], width=48)
        st.markdown(f"**{jogo['time_fora']}**")

    # Converte para datetime nativo (garantido)
    data_jogo = pd.to_datetime(jogo["data_hora"]).to_pydatetime()

    st.caption(f"📅 {data_jogo.strftime('%d/%m/%Y %H:%M')} | 🧩 Grupo {jogo['grupo']}")

    if st.button(f"💬 Palpite - {jogo['time_casa']} x {jogo['time_fora']}", key=f"palpite_{jogo['id']}"):
        if not st.session_state.get("logged_in", False):
            st.warning("Efetue o seu cadastro para participar do bolão.")
            st.session_state["menu"] = "Login"
            st.rerun()
        else:
            # Limite de 45 minutos antes do jogo
            limite = data_jogo - timedelta(minutes=45)
            agora = datetime.now()

            # Agora e limite são ambos datetime.datetime
            if agora > limite:
                st.error("⏰ Palpites encerrados para este jogo.")
            else:
                st.session_state["jogo_selecionado"] = jogo["id"]
                st.session_state["menu"] = "Palpite"
                st.rerun()

    st.markdown("---")
