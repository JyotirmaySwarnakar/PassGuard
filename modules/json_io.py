import json
import os
from modules.db import get_credentials, add_credential
from modules.crypto_utils import encrypt_data, decrypt_data, get_fernet

def export_credentials_json(filepath):
    dir_path = os.path.dirname(filepath) or '.'
    if os.path.isdir(filepath):
        print("❌ Please provide a full file path, not a directory.")
        return
    creds = get_credentials()
    data = [
        {"service": s, "username": u, "password": p}
        for s, u, p in creds
    ]
    fernet = get_fernet()
    encrypted = fernet.encrypt(json.dumps(data).encode())
    try:
        with open(filepath, "wb") as f:
            f.write(encrypted)
        print(f"[✓] Exported {len(data)} credentials to {filepath} (encrypted)")
    except Exception as e:
        print(f"❌ Failed to export credentials: {e}")

def import_credentials_json(filepath):
    dir_path = os.path.dirname(filepath) or '.'
    if os.path.isdir(filepath):
        print("❌ Please provide a full file path, not a directory.")
        return
    fernet = get_fernet()
    try:
        with open(filepath, "rb") as f:
            encrypted = f.read()
        data = json.loads(fernet.decrypt(encrypted).decode())
    except Exception as e:
        print(f"❌ Failed to import credentials: {e}")
        return
    count = 0
    for entry in data:
        try:
            add_credential(entry["service"], entry["username"], entry["password"])
            count += 1
        except Exception as e:
            print(f"Skipped {entry['service']}: {e}")
    print(f"[✓] Imported {count} credentials from {filepath}")