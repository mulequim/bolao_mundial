import bcrypt

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha com bcrypt"""
    return bcrypt.checkpw(password.encode(), hashed.encode())
