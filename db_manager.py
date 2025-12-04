import streamlit as st
import pandas as pd

def get_conn():
    """Retorna conexão ativa do Streamlit com o PostgreSQL."""
    return st.connection("postgresql", type="sql")


# ================================
#         TABELA: usuarios
# ================================
def get_usuarios():
    conn = get_conn()
    df = conn.query("SELECT * FROM usuarios ORDER BY id;")
    return df


def add_usuario(nome, email):
    conn = get_conn()
    conn.query(
        "INSERT INTO usuarios (nome, email) VALUES (%s, %s);",
        params=(nome, email)
    )


# ================================
#         TABELA: jogos
# ================================
def get_jogos():
    conn = get_conn()
    return conn.query("SELECT * FROM jogos ORDER BY id;")


# ================================
#         TABELA: palpites
# ================================
def salvar_palpite(id_usuario, id_jogo, palpite_time1, palpite_time2):
    conn = get_conn()
    conn.query(
        """
        INSERT INTO palpites (id_usuario, id_jogo, palpite_time1, palpite_time2)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_usuario, id_jogo)
        DO UPDATE SET
            palpite_time1 = EXCLUDED.palpite_time1,
            palpite_time2 = EXCLUDED.palpite_time2;
        """,
        params=(id_usuario, id_jogo, palpite_time1, palpite_time2),
    )


def get_palpite_usuario(id_usuario):
    conn = get_conn()
    return conn.query(
        "SELECT * FROM palpites WHERE id_usuario = %s;",
        params=(id_usuario,)
    )


# ================================
#         TABELA: pontuacao
# ================================
def get_pontuacao():
    conn = get_conn()
    return conn.query("SELECT * FROM pontuacao ORDER BY pontos DESC;")


def atualizar_pontos(id_usuario, pontos):
    conn = get_conn()
    conn.query(
        """
        INSERT INTO pontuacao (id_usuario, pontos)
        VALUES (%s, %s)
        ON CONFLICT (id_usuario)
        DO UPDATE SET
            pontos = EXCLUDED.pontos;
        """,
        params=(id_usuario, pontos)
    )
