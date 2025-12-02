from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet():
    return Fernet(settings.ENCRYPT_KEY)

def encrypt_id(pk: int) -> str:
    """Cifra un ID"""
    fernet = get_fernet()
    return fernet.encrypt(str(pk).encode()).decode()

def decrypt_id(token: str) -> int:
    """Descifra un token a su ID"""
    fernet = get_fernet()
    return int(fernet.decrypt(token.encode()).decode())
