# modules/auth.py

import os
import bcrypt
import getpass
from .config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from .utils import set_secure_permissions

def check_or_create_master_password():
    """
    Checks for existing master password hash. If not present, creates one.
    Then asks the user to authenticate.
    """
    if not os.path.exists(MASTER_PASSWORD_FILE):
        print("[!] No master password set. Creating new master password.")
        while True:
            password = getpass.getpass("Set new master password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password == confirm:
                break
            print("Passwords do not match. Try again.")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        with open(MASTER_PASSWORD_FILE, "wb") as f:
            f.write(hashed)
        set_secure_permissions(MASTER_PASSWORD_FILE)
        print("[✓] Master password set.")
    else:
        # Authenticate
        with open(MASTER_PASSWORD_FILE, "rb") as f:
            stored_hash = f.read()
        for _ in range(3):
            password = getpass.getpass("Enter master password: ")
            if bcrypt.checkpw(password.encode(), stored_hash):
                print("[✓] Authentication successful.")
                return True
            else:
                print("❌ Incorrect password.")
        print("❌ Too many failed attempts. Exiting.")
        return False
    return True
