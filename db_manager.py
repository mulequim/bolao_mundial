import streamlit as st
import psycopg2

def get_connection():
    conf = st.secrets["database"]
    return psycopg2.connect(
        host=conf["host"],
        port=conf["port"],
        database=conf["database"],
        user=conf["user"],
        password=conf["password"],
        sslmode=conf["sslmode"]
    )
