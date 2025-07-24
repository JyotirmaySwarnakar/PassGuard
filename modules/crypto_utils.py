#!/usr/bin/env python3
"""
Cryptographic Utilities Module
Handles encryption, decryption, and key management using Fernet (AES-256).
"""

import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from .config import FERNET_KEY_FILE
from .utils import set_secure_permissions

class CryptoManager:
    """Manages cryptographic operations for the password manager."""
    
    def __init__(self):
        self._fernet = None
    
    def _generate_key(self):
        """Generate a new Fernet encryption key."""
        try:
            key = Fernet.generate_key()
            with open(FERNET_KEY_FILE, "wb") as f:
                f.write(key)
            set_secure_permissions(FERNET_KEY_FILE)
            print("🔑 New encryption key generated.")
        except Exception as e:
            raise Exception(f"Failed to generate encryption key: {e}")
    
    def _load_key(self):
        """Load the Fernet encryption key from file."""
        if not os.path.exists(FERNET_KEY_FILE):
            self._generate_key()
        
        try:
            with open(FERNET_KEY_FILE, "rb") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load encryption key: {e}")
    
    def get_fernet(self):
        """Get Fernet instance, creating it if necessary."""
        if self._fernet is None:
            key = self._load_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt string data using Fernet.
        
        Args:
            data (str): Plain text data to encrypt
            
        Returns:
            str: Base64 encoded encrypted data
            
        Raises:
            Exception: If encryption fails
        """
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        try:
            fernet = self.get_fernet()
            encrypted_bytes = fernet.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt Fernet encrypted data.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            
        Returns:
            str: Decrypted plain text
            
        Raises:
            Exception: If decryption fails
        """
        if not isinstance(encrypted_data, str):
            raise ValueError("Encrypted data must be a string")
        
        try:
            fernet = self.get_fernet()
            decrypted_bytes = fernet.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")

# Global instance for backward compatibility
_crypto_manager = CryptoManager()

# Legacy functions for backward compatibility
def generate_key():
    """Generate a new encryption key (legacy function)."""
    return _crypto_manager._generate_key()

def load_key():
    """Load encryption key (legacy function)."""
    return _crypto_manager._load_key()

def get_fernet():
    """Get Fernet instance (legacy function)."""
    return _crypto_manager.get_fernet()

def encrypt_data(data: str) -> str:
    """Encrypt data (legacy function)."""
    return _crypto_manager.encrypt_data(data)

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data (legacy function)."""
    return _crypto_manager.decrypt_data(encrypted_data)