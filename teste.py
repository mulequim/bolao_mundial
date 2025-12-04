import streamlit as st

conn = st.connection("postgresql", type="sql")

st.write(conn.query("SELECT NOW();"))
