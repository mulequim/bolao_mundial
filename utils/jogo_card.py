# utils/jogo_card.py
import streamlit as st
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

    st.caption(f"📅 {jogo['data_hora'].strftime('%d/%m/%Y %H:%M')} | 🧩 Grupo {jogo['grupo']}")

    # Botão de palpite
    if st.button(f"💬 Palpite - {jogo['time_casa']} x {jogo['time_fora']}", key=f"palpite_{jogo['id']}"):
        if not st.session_state.get("logged_in", False):
            st.warning("Efetue o seu cadastro para participar do bolão.")
            st.session_state["menu"] = "Login"
            st.rerun()
        else:
            # Verifica se ainda está dentro do prazo (até 45min antes do jogo)
            limite = jogo["data_hora"] - timedelta(minutes=45)
            if datetime.now() > limite:
                st.error("⏰ Palpites encerrados para este jogo.")
            else:
                st.session_state["jogo_selecionado"] = jogo["id"]
                st.session_state["menu"] = "Palpite"
                st.rerun()

    st.markdown("---")
