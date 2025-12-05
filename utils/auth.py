import hashlib

def hash_password(password: str) -> str:
    """Retorna o hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return hash_password(password) == hashed
