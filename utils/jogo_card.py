# utils/jogo_card.py
import streamlit as st

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

    st.caption(f"📅 {jogo['data_hora'].strftime('%d/%m/%Y')} | ⏰ A confirmar")
    st.caption(f"🏷️ Grupo {jogo['grupo']}")

    if st.button(f"💬 Palpite - {jogo['time_casa']} x {jogo['time_fora']}", key=f"palpite_{jogo['id']}"):
        st.session_state["jogo_selecionado"] = jogo["id"]
        st.session_state["menu"] = "Palpite"
        st.rerun()

    st.markdown("---")
