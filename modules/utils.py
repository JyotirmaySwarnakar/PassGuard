# modules/utils.py

import os
from modules.config import FILE_PERMISSION, FOLDER_PERMISSION, SECURE_FOLDER

def set_secure_permissions(path):
    os.chmod(path, FILE_PERMISSION)

def ensure_secure_folder():
    if not os.path.exists(SECURE_FOLDER):
        os.makedirs(SECURE_FOLDER)
        os.chmod(SECURE_FOLDER, FOLDER_PERMISSION)

def load_session_timeout(default=180):
    from modules.config import SESSION_TIMEOUT_FILE
    try:
        if os.path.exists(SESSION_TIMEOUT_FILE):
            with open(SESSION_TIMEOUT_FILE, "r") as f:
                return int(f.read().strip())
    except Exception:
        pass
    return default

def save_session_timeout(timeout):
    from modules.config import SESSION_TIMEOUT_FILE
    with open(SESSION_TIMEOUT_FILE, "w") as f:
        f.write(str(timeout))
