import pandas as pd
from sqlalchemy import text
from db_manager import DBManager

db = DBManager()

def create_palpite(user_id: int, jogo_id: int, palpite_casa: int, palpite_fora: int) -> bool:
    try:
        with db.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO palpites (user_id, jogo_id, palpite_casa, palpite_fora) "
                     "VALUES (:user_id, :jogo_id, :palpite_casa, :palpite_fora)"),
                {"user_id": user_id, "jogo_id": jogo_id, "palpite_casa": palpite_casa, "palpite_fora": palpite_fora}
            )
        return True
    except Exception as e:
        print(f"Erro ao registrar palpite: {e}")
        return False

def read_palpites_by_user(user_id: int) -> pd.DataFrame:
    try:
        query = text("SELECT * FROM palpites WHERE user_id = :user_id")
        return pd.read_sql(query, db.engine, params={"user_id": user_id})
    except Exception as e:
        print(f"Erro ao buscar palpites: {e}")
        return pd.DataFrame()
