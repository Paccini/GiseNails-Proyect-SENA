from django import template
from cryptography.fernet import Fernet
from django.conf import settings

register = template.Library()
fernet = Fernet(settings.ENCRYPT_KEY)

@register.filter
def encrypt_id(pk):
    return fernet.encrypt(str(pk).encode()).decode()

@register.filter
def decrypt_id(token):
    return int(fernet.decrypt(token.encode()).decode())
