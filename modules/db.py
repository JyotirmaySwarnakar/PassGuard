#!/usr/bin/env python3
"""
Database Management Module
Handles SQLite database operations for credential storage with encryption.
Simplified version without duplicate detection for imports.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Tuple, Optional
from .config import DATABASE_FILE
from .utils import set_secure_permissions
from .crypto_utils import encrypt_data, decrypt_data

class DuplicateCredentialError(Exception):
    """Raised when attempting to add duplicate credentials."""
    def __init__(self, service: str, username: str):
        self.service = service
        self.username = username
        super().__init__(f"Credential for {service} with username {username} already exists")

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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create unique index for service + username combination
                cursor.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_service_username 
                    ON credentials(service, username)
                ''')
                
                # Create index for faster searches
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_service 
                    ON credentials(service)
                ''')
                
                conn.commit()
                print("🗄️  Database initialized successfully.")
            
            set_secure_permissions(self.db_file)
    
    def credential_exists(self, service: str, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a credential already exists (case-insensitive).
        
        Args:
            service (str): Service name
            username (str): Username/email
            exclude_id (Optional[int]): ID to exclude from check (for editing)
            
        Returns:
            bool: True if credential exists, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if exclude_id is not None:
                    cursor.execute('''
                        SELECT COUNT(*) FROM credentials 
                        WHERE LOWER(service) = LOWER(?) AND username = ? AND id != ?
                    ''', (service.strip(), encrypt_data(username.strip()), exclude_id))
                else:
                    cursor.execute('''
                        SELECT COUNT(*) FROM credentials 
                        WHERE LOWER(service) = LOWER(?) AND username = ?
                    ''', (service.strip(), encrypt_data(username.strip())))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            return False
    
    def get_existing_credential(self, service: str, username: str) -> Optional[Tuple[str, str, str]]:
        """
        Get existing credential details.
        
        Args:
            service (str): Service name
            username (str): Username/email
            
        Returns:
            Optional[Tuple[str, str, str]]: (service, username, password) if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT service, username, password FROM credentials 
                    WHERE LOWER(service) = LOWER(?) AND username = ?
                ''', (service.strip(), encrypt_data(username.strip())))
                result = cursor.fetchone()
                
                if result:
                    service, enc_username, enc_password = result
                    return (service, decrypt_data(enc_username), decrypt_data(enc_password))
                return None
        except Exception:
            return None
    
    def add_credential(self, service: str, username: str, password: str, allow_duplicates: bool = False):
        """
        Add a new credential to the database.
        
        Args:
            service (str): Service name
            username (str): Username/email
            password (str): Password (will be encrypted)
            allow_duplicates (bool): If True, skip duplicate check
            
        Raises:
            ValueError: If any field is empty
            DuplicateCredentialError: If credential already exists and duplicates not allowed
            Exception: If database operation fails
        """
        # Validate input
        if not all([service.strip(), username.strip(), password.strip()]):
            raise ValueError("Service, username, and password cannot be empty.")
        
        service = service.strip()
        username = username.strip()
        password = password.strip()
        
        # Check for duplicates if not allowed
        if not allow_duplicates and self.credential_exists(service, username):
            raise DuplicateCredentialError(service, username)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO credentials (service, username, password)
                    VALUES (?, ?, ?)
                ''', (service, encrypt_data(username), encrypt_data(password)))
                conn.commit()
        except sqlite3.IntegrityError:
            # This handles database-level constraints
            if not allow_duplicates:
                raise DuplicateCredentialError(service, username)
            # If duplicates are allowed, we could try to update instead
            # but for simplicity, we'll just ignore the error
            pass
        except Exception as e:
            raise Exception(f"Failed to add credential: {e}")
    
    def update_credential(self, service: str, username: str, new_password: str):
        """
        Update an existing credential's password.
        
        Args:
            service (str): Service name
            username (str): Username/email
            new_password (str): New password
            
        Returns:
            bool: True if credential was updated, False if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE credentials
                    SET password = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE LOWER(service) = LOWER(?) AND username = ?
                ''', (encrypt_data(new_password), service.strip(), encrypt_data(username.strip())))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Failed to update credential: {e}")
    
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
                    ORDER BY LOWER(service), LOWER(username)
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
    
    def get_credential_by_index(self, index: int) -> Optional[Tuple[int, str, str, str]]:
        """
        Get credential by index (1-based).
        
        Args:
            index (int): 1-based index of credential
            
        Returns:
            Optional[Tuple[int, str, str, str]]: (id, service, username, password) if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, service, username, password 
                    FROM credentials 
                    ORDER BY LOWER(service), LOWER(username)
                ''')
                records = cursor.fetchall()
                
                if index < 1 or index > len(records):
                    return None
                
                record = records[index - 1]
                cred_id, service, enc_username, enc_password = record
                
                return (cred_id, service, decrypt_data(enc_username), decrypt_data(enc_password))
        except Exception:
            return None
    
    def edit_credential(self, index: int, new_service: str, new_username: str, new_password: str):
        """
        Edit an existing credential by index.
        
        Args:
            index (int): 1-based index of credential to edit
            new_service (str): New service name
            new_username (str): New username
            new_password (str): New password
            
        Raises:
            IndexError: If index is invalid
            ValueError: If new values are empty
            DuplicateCredentialError: If new service+username combination already exists
            Exception: If database operation fails
        """
        if not all([new_service.strip(), new_username.strip(), new_password.strip()]):
            raise ValueError("Service, username, and password cannot be empty.")
        
        new_service = new_service.strip()
        new_username = new_username.strip()
        new_password = new_password.strip()
        
        # Get the credential to edit
        credential = self.get_credential_by_index(index)
        if credential is None:
            raise IndexError("Invalid credential index.")
        
        cred_id, current_service, current_username, current_password = credential
        
        # Check if we're changing to a duplicate (excluding current record)
        if (new_service.lower() != current_service.lower() or 
            new_username.lower() != current_username.lower()):
            if self.credential_exists(new_service, new_username, exclude_id=cred_id):
                raise DuplicateCredentialError(new_service, new_username)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Update the credential
                cursor.execute('''
                    UPDATE credentials
                    SET service = ?, username = ?, password = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_service, encrypt_data(new_username), encrypt_data(new_password), cred_id))
                
                conn.commit()
                
                if cursor.rowcount == 0:
                    raise Exception("No credential was updated.")
                    
        except sqlite3.IntegrityError:
            raise DuplicateCredentialError(new_service, new_username)
        except DuplicateCredentialError:
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
        # Get the credential to delete
        credential = self.get_credential_by_index(index)
        if credential is None:
            raise IndexError("Invalid credential index.")
        
        cred_id = credential[0]
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete the credential
                cursor.execute('DELETE FROM credentials WHERE id = ?', (cred_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    raise Exception("No credential was deleted.")
                    
        except Exception as e:
            raise Exception(f"Failed to remove credential: {e}")
    
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

def add_credential(service: str, username: str, password: str, allow_duplicates: bool = False):
    """Add credential (legacy function)."""
    return _db_manager.add_credential(service, username, password, allow_duplicates)

def get_credentials() -> List[Tuple[str, str, str]]:
    """Get credentials (legacy function)."""
    return _db_manager.get_credentials()

def edit_credential(index: int, new_service: str, new_username: str, new_password: str):
    """Edit credential (legacy function)."""
    return _db_manager.edit_credential(index, new_service, new_username, new_password)

def remove_credential(index: int):
    """Remove credential (legacy function)."""
    return _db_manager.remove_credential(index)

def credential_exists(service: str, username: str) -> bool:
    """Check if credential exists (legacy function)."""
    return _db_manager.credential_exists(service, username)