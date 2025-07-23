import os
import pyotp
from modules.config import SECURE_FOLDER

TOTP_SECRET_FILE = os.path.join(SECURE_FOLDER, ".totp_secret")

def is_totp_enabled():
    return os.path.exists(TOTP_SECRET_FILE)

def enable_totp():
    if not is_totp_enabled():
        secret = pyotp.random_base32()
        with open(TOTP_SECRET_FILE, "w") as f:
            f.write(secret)
        print(f"[!] TOTP enabled. Scan this secret in your authenticator app:\n{secret}")
    else:
        print("[!] TOTP is already enabled.")

def disable_totp():
    if is_totp_enabled():
        os.remove(TOTP_SECRET_FILE)
        print("[✓] TOTP disabled.")
    else:
        print("[!] TOTP is not enabled.")

def get_or_create_totp_secret():
    if not is_totp_enabled():
        enable_totp()
    with open(TOTP_SECRET_FILE, "r") as f:
        secret = f.read().strip()
    return secret

def verify_totp(code):
    if not is_totp_enabled():
        print("❌ TOTP is not enabled.")
        return False
    secret = get_or_create_totp_secret()
    totp = pyotp.TOTP(secret)
    return totp.verify(code)