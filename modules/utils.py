# modules/utils.py

import os
from modules.config import FILE_PERMISSION, FOLDER_PERMISSION, SECURE_FOLDER

def set_secure_permissions(path):
    os.chmod(path, FILE_PERMISSION)

def ensure_secure_folder():
    if not os.path.exists(SECURE_FOLDER):
        os.makedirs(SECURE_FOLDER)
        os.chmod(SECURE_FOLDER, FOLDER_PERMISSION)
