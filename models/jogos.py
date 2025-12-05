import pandas as pd
from sqlalchemy import text
from db_manager import DBManager

db = DBManager()

def create_game(time_casa: str, time_fora: str, data_hora: str, status: str) -> bool:
    try:
        with db.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO jogos (time_casa, time_fora, data_hora, status) "
                     "VALUES (:time_casa, :time_fora, :data_hora, :status)"),
                {"time_casa": time_casa, "time_fora": time_fora, "data_hora": data_hora, "status": status}
            )
        return True
    except Exception as e:
        print(f"Erro ao criar jogo: {e}")
        return False

def read_games() -> pd.DataFrame:
    try:
        return pd.read_sql("SELECT * FROM jogos ORDER BY data_hora;", db.engine)
    except Exception as e:
        print(f"Erro ao listar jogos: {e}")
        return pd.DataFrame()
