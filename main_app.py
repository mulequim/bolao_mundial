import streamlit as st
from models.usuarios import read_users, create_user
from models.jogos import read_games

st.title("Bolão Mundial 2026")

st.subheader("Usuários")
st.write(read_users())

if st.button("Criar usuário de teste"):
    create_user("teste", "Usuário Teste", "hash123", "player", "teste@email.com")
    st.success("Usuário criado!")

st.subheader("Jogos")
st.write(read_games())
