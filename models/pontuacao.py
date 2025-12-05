import pandas as pd
from sqlalchemy import text
from db_manager import DBManager

db = DBManager()

def create_pontuacao(user_id: int, pontos_total: int) -> bool:
    try:
        with db.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO pontuacao (user_id, pontos_total) VALUES (:user_id, :pontos_total)"),
                {"user_id": user_id, "pontos_total": pontos_total}
            )
        return True
    except Exception as e:
        print(f"Erro ao criar pontuação: {e}")
        return False

def read_pontuacoes() -> pd.DataFrame:
    try:
        return pd.read_sql("SELECT * FROM pontuacao ORDER BY pontos_total DESC;", db.engine)
    except Exception as e:
        print(f"Erro ao listar pontuações: {e}")
        return pd.DataFrame()
