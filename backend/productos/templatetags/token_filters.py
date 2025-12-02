from django import template
from django.conf import settings
from cryptography.fernet import Fernet

register = template.Library()

# Usa la misma clave que usas para encrypt/decrypt
fernet = Fernet(settings.ENCRYPT_KEY)

@register.filter(name='encrypt_id')
def encrypt_id(value):
    """
    Encripta un ID para usarlo en URLs.
    """
    try:
        value = str(value).encode()
        token = fernet.encrypt(value)
        return token.decode()
    except Exception:
        return ""