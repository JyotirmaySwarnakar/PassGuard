#!/usr/bin/env python3
"""
Database Management Module
Handles SQLite database operations for credential storage with encryption.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Tuple
from .config import DATABASE_FILE
from .utils import set_secure_permissions
from .crypto_utils import encrypt_data, decrypt_data

class DatabaseManager:
    """Manages database operations for the password manager."""
    
    def __init__(self):
        self.db_file = DATABASE_FILE
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def initialize_db(self):
        """Initialize the database with required tables."""
        if not os.path.exists(self.db_file):
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create credentials table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS credentials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service TEXT NOT NULL,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster searches
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_service 
                    ON credentials(service)
                ''')
                
                conn.commit()
                print("🗄️  Database initialized successfully.")
            
            set_secure_permissions(self.db_file)
    
    def add_credential(self, service: str, username: str, password: str):
        """
        Add a new credential to the database.
        
        Args:
            service (str): Service name
            username (str): Username/email
            password (str): Password (will be encrypted)
            
        Raises:
            ValueError: If any field is empty
            Exception: If database operation fails
        """
        # Validate input
        if not all([service.strip(), username.strip(), password.strip()]):
            raise ValueError("Service, username, and password cannot be empty.")
        
        # Check for duplicates
        if self._credential_exists(service, username):
            raise ValueError(f"Credential for {service} with username {username} already exists.")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO credentials (service, username, password)
                    VALUES (?, ?, ?)
                ''', (service.strip(), encrypt_data(username), encrypt_data(password)))
                conn.commit()
        except Exception as e:
            raise Exception(f"Failed to add credential: {e}")
    
    def get_credentials(self) -> List[Tuple[str, str, str]]:
        """
        Retrieve all credentials from the database.
        
        Returns:
            List[Tuple[str, str, str]]: List of (service, username, password) tuples
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT service, username, password 
                    FROM credentials 
                    ORDER BY service, username
                ''')
                records = cursor.fetchall()
                
                # Decrypt usernames and passwords
                return [
                    (service, decrypt_data(username), decrypt_data(password))
                    for service, username, password in records
                ]
        except Exception as e:
            print(f"❌ Failed to retrieve credentials: {e}")
            return []
    
    def edit_credential(self, index: int, new_service: str, new_username: str, new_password: str):
        """
        Edit an existing credential.
        
        Args:
            index (int): 1-based index of credential to edit
            new_service (str): New service name
            new_username (str): New username
            new_password (str): New password
            
        Raises:
            IndexError: If index is invalid
            ValueError: If new values are empty
            Exception: If database operation fails
        """
        if not all([new_service.strip(), new_username.strip(), new_password.strip()]):
            raise ValueError("Service, username, and password cannot be empty.")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all credential IDs
                cursor.execute('SELECT id FROM credentials ORDER BY service, username')
                ids = [row[0] for row in cursor.fetchall()]
                
                if index < 1 or index > len(ids):
                    raise IndexError("Invalid credential index.")
                
                cred_id = ids[index - 1]
                
                # Update the credential
                cursor.execute('''
                    UPDATE credentials
                    SET service = ?, username = ?, password = ?
                    WHERE id = ?
                ''', (new_service.strip(), encrypt_data(new_username), encrypt_data(new_password), cred_id))
                
                conn.commit()
                
                if cursor.rowcount == 0:
                    raise Exception("No credential was updated.")
                    
        except IndexError:
            raise
        except Exception as e:
            raise Exception(f"Failed to edit credential: {e}")
    
    def remove_credential(self, index: int):
        """
        Remove a credential from the database.
        
        Args:
            index (int): 1-based index of credential to remove
            
        Raises:
            IndexError: If index is invalid
            Exception: If database operation fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all credential IDs
                cursor.execute('SELECT id FROM credentials ORDER BY service, username')
                ids = [row[0] for row in cursor.fetchall()]
                
                if index < 1 or index > len(ids):
                    raise IndexError("Invalid credential index.")
                
                cred_id = ids[index - 1]
                
                # Delete the credential
                cursor.execute('DELETE FROM credentials WHERE id = ?', (cred_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    raise Exception("No credential was deleted.")
                    
        except IndexError:
            raise
        except Exception as e:
            raise Exception(f"Failed to remove credential: {e}")
    
    def _credential_exists(self, service: str, username: str) -> bool:
        """
        Check if a credential already exists.
        
        Args:
            service (str): Service name
            username (str): Username
            
        Returns:
            bool: True if credential exists, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM credentials 
                    WHERE service = ? AND username = ?
                ''', (service, encrypt_data(username)))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            return False
    
    def get_credential_count(self) -> int:
        """
        Get the total number of stored credentials.
        
        Returns:
            int: Number of credentials
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM credentials')
                return cursor.fetchone()[0]
        except Exception:
            return 0

# Global instance for backward compatibility
_db_manager = DatabaseManager()

# Legacy functions for backward compatibility
def initialize_db():
    """Initialize database (legacy function)."""
    return _db_manager.initialize_db()

def add_credential(service: str, username: str, password: str):
    """Add credential (legacy function)."""
    return _db_manager.add_credential(service, username, password)

def get_credentials() -> List[Tuple[str, str, str]]:
    """Get credentials (legacy function)."""
    return _db_manager.get_credentials()

def edit_credential(index: int, new_service: str, new_username: str, new_password: str):
    """Edit credential (legacy function)."""
    return _db_manager.edit_credential(index, new_service, new_username, new_password)

def remove_credential(index: int):
    """Remove credential (legacy function)."""
    return _db_manager.remove_credential(index)