import pandas as pd
from sqlalchemy import text
from db_manager import DBManager
import pytz

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


def read_all_games() -> pd.DataFrame:
    try:
        query = text("SELECT * FROM jogos ORDER BY data_hora;")
        df = pd.read_sql(query, db.engine)

        # Converte a coluna data_hora para datetime com timezone
        tz = pytz.timezone("America/Sao_Paulo")
        df["data_hora"] = pd.to_datetime(df["data_hora"]).dt.tz_convert(tz)

        return df
    except Exception as e:
        print(f"Erro ao listar jogos: {e}")
        return pd.DataFrame()

def read_game_by_id(jogo_id: int) -> dict | None:
    try:
        query = text("SELECT * FROM jogos WHERE id = :id")
        df = pd.read_sql(query, db.engine, params={"id": jogo_id})
        if df.empty:
            return None

        jogo = df.iloc[0].to_dict()

        # Converte data_hora para datetime com timezone
        tz = pytz.timezone("America/Sao_Paulo")
        jogo["data_hora"] = pd.to_datetime(jogo["data_hora"]).tz_convert(tz).to_pydatetime()

        return jogo
    except Exception as e:
        print(f"Erro ao buscar jogo por id: {e}")
        return None
        jogo = df.iloc[0].to_dict()

        # Converte data_hora para datetime com timezone
        tz = pytz.timezone("America/Sao_Paulo")
        jogo["data_hora"] = pd.to_datetime(jogo["data_hora"]).tz_convert(tz).to_pydatetime()

        return jogo
    except Exception as e:
        print(f"Erro ao buscar jogo por id: {e}")
        return None

