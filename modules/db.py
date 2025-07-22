# modules/db.py

import sqlite3
import os
from modules.config import DATABASE_FILE
from modules.utils import set_secure_permissions
from modules.crypto_utils import encrypt_data, decrypt_data

def initialize_db():
    if not os.path.exists(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        set_secure_permissions(DATABASE_FILE)

def add_credential(service, username, password):
    if not service.strip() or not username.strip() or not password.strip():
        raise ValueError("Service, username, and password cannot be empty.")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO credentials (service, username, password)
        VALUES (?, ?, ?)
    ''', (service, encrypt_data(username), encrypt_data(password)))
    conn.commit()
    conn.close()

def get_credentials():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT service, username, password FROM credentials')
    records = c.fetchall()
    conn.close()
    return [(s, decrypt_data(u), decrypt_data(p)) for s, u, p in records]

def edit_credential(index, new_service, new_username, new_password):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT id FROM credentials')
    ids = [row[0] for row in c.fetchall()]
    if index < 1 or index > len(ids):
        conn.close()
        raise IndexError("Invalid credential index.")
    cred_id = ids[index - 1]
    c.execute('''
        UPDATE credentials
        SET service = ?, username = ?, password = ?
        WHERE id = ?
    ''', (new_service, encrypt_data(new_username), encrypt_data(new_password), cred_id))
    conn.commit()
    conn.close()

def remove_credential(index):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT id FROM credentials')
    ids = [row[0] for row in c.fetchall()]
    if index < 1 or index > len(ids):
        conn.close()
        raise IndexError("Invalid credential index.")
    cred_id = ids[index - 1]
    c.execute('DELETE FROM credentials WHERE id = ?', (cred_id,))
    conn.commit()
    conn.close()
