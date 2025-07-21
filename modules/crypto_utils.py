# modules/crypto_utils.py

from cryptography.fernet import Fernet
import os
from modules.config import FERNET_KEY_FILE
from modules.utils import set_secure_permissions

def generate_key():
    key = Fernet.generate_key()
    with open(FERNET_KEY_FILE, "wb") as f:
        f.write(key)
    set_secure_permissions(FERNET_KEY_FILE)

def load_key():
    if not os.path.exists(FERNET_KEY_FILE):
        generate_key()
    with open(FERNET_KEY_FILE, "rb") as f:
        return f.read()

def get_fernet():
    key = load_key()
    return Fernet(key)

def encrypt_data(data: str) -> str:
    fernet = get_fernet()
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    fernet = get_fernet()
    return fernet.decrypt(token.encode()).decode()
