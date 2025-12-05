import pandas as pd
from sqlalchemy import text
from db_manager import DBManager

db = DBManager()

def create_user(username: str, name: str, password_hash: str, function: str, email: str) -> bool:
    try:
        with db.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO usuarios (username, name, password_hash, function, email, created_at) "
                     "VALUES (:username, :name, :password_hash, :function, :email, NOW())"),
                {"username": username, "name": name, "password_hash": password_hash, "function": function, "email": email}
            )
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False

def read_users() -> pd.DataFrame:
    try:
        return pd.read_sql("SELECT * FROM usuarios ORDER BY created_at DESC;", db.engine)
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return pd.DataFrame()
