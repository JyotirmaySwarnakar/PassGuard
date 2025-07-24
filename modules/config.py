# modules/config.py

import os

# User's home directory
HOME_DIR = os.path.expanduser("~")

# Secure app data folder
SECURE_FOLDER = os.path.join(HOME_DIR, ".PassGuard")

# Files
MASTER_PASSWORD_FILE = os.path.join(SECURE_FOLDER, ".master")
FERNET_KEY_FILE = os.path.join(SECURE_FOLDER, ".fernet_key")
DATABASE_FILE = os.path.join(SECURE_FOLDER, "passwords.db")
SESSION_TIMEOUT_FILE = os.path.join(SECURE_FOLDER, ".session_timeout")

# Permissions
FOLDER_PERMISSION = 0o700  # Only owner can access folder
FILE_PERMISSION = 0o600    # Only owner can read/write
