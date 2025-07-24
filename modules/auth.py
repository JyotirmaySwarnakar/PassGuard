#!/usr/bin/env python3
"""
Authentication Module
Handles master password creation, verification, and authentication logic.
"""

import os
import bcrypt
import getpass
import secrets
from typing import Optional
from .config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from .utils import set_secure_permissions
from .totp_utils import is_totp_enabled, verify_totp

class AuthenticationManager:
    """Manages authentication operations for the password manager."""
    
    def __init__(self):
        self.master_file = MASTER_PASSWORD_FILE
        self.max_attempts = 3
    
    def _ensure_secure_folder(self):
        """Ensure the secure folder exists with proper permissions."""
        if not os.path.exists(SECURE_FOLDER):
            os.makedirs(SECURE_FOLDER, mode=0o700)
        else:
            os.chmod(SECURE_FOLDER, 0o700)
    
    def _create_master_password(self) -> bool:
        """
        Create a new master password.
        
        Returns:
            bool: True if password was created successfully, False otherwise
        """
        print("🔐 Setting up your master password")
        print("💡 Choose a strong password (8+ characters, mix of letters, numbers, symbols)")
        print("-" * 60)
        
        while True:
            password = getpass.getpass("🔑 New master password: ")
            confirm = getpass.getpass("🔑 Confirm password: ")
            
            if password != confirm:
                print("❌ Passwords don't match. Please try again.")
                continue
            
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long.")
                continue
                
            # Check password strength
            strength_score = self._calculate_password_strength(password)
            if strength_score < 3:
                print("⚠️  Weak password detected!")
                print("💡 Consider using: uppercase, lowercase, numbers, and symbols")
                use_weak = input("Continue with weak password anyway? (y/N): ")
                if use_weak.lower() != 'y':
                    continue
            
            break
        
        try:
            # Hash password with bcrypt
            salt = bcrypt.gensalt(rounds=12)  # Higher cost factor for security
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Save to file
            with open(self.master_file, "wb") as f:
                f.write(hashed)
            
            set_secure_permissions(self.master_file)
            print("✅ Master password created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create master password: {e}")
            return False
    
    def _calculate_password_strength(self, password: str) -> int:
        """
        Calculate password strength score (0-5).
        
        Args:
            password (str): Password to evaluate
            
        Returns:
            int: Strength score (0=very weak, 5=very strong)
        """
        score = 0
        
        # Length check
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Character variety checks
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        return min(score, 5)
    
    def _verify_master_password(self) -> bool:
        """
        Verify the master password with user input.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not os.path.exists(self.master_file):
            print("❌ Master password file not found!")
            return False
        
        try:
            with open(self.master_file, "rb") as f:
                stored_hash = f.read()
        except Exception as e:
            print(f"❌ Failed to read master password file: {e}")
            return False
        
        print("🔐 Authentication Required")
        print("-" * 25)
        
        for attempt in range(self.max_attempts):
            try:
                password = getpass.getpass("🔑 Master password: ")
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    # Check for 2FA if enabled
                    if is_totp_enabled():
                        if not self._verify_2fa():
                            return False
                    
                    print("✅ Authentication successful!")
                    return True
                else:
                    attempts_left = self.max_attempts - attempt - 1
                    if attempts_left > 0:
                        print(f"❌ Incorrect password. {attempts_left} attempt(s) remaining.")
                    else:
                        print("❌ Too many failed attempts. Access denied.")
                        
            except KeyboardInterrupt:
                print("\n⚠️  Authentication cancelled.")
                return False
            except Exception as e:
                print(f"❌ Authentication error: {e}")
                return False
        
        return False
    
    def _verify_2fa(self) -> bool:
        """
        Verify 2FA TOTP code.
        
        Returns:
            bool: True if 2FA verification successful, False otherwise
        """
        print("🔒 Two-Factor Authentication Required")
        print("📱 Enter the 6-digit code from your authenticator app")
        
        for attempt in range(3):
            try:
                code = input("🔢 2FA Code: ").strip()
                
                if len(code) != 6 or not code.isdigit():
                    print("❌ Invalid format. Please enter a 6-digit code.")
                    continue
                
                if verify_totp(code):
                    print("✅ 2FA verification successful!")
                    return True
                else:
                    attempts_left = 2 - attempt
                    if attempts_left > 0:
                        print(f"❌ Invalid 2FA code. {attempts_left} attempt(s) remaining.")
                    else:
                        print("❌ Too many failed 2FA attempts.")
                        
            except KeyboardInterrupt:
                print("\n⚠️  2FA verification cancelled.")
                return False
            except Exception as e:
                print(f"❌ 2FA verification error: {e}")
                return False
        
        return False
    
    def check_or_create_master_password(self) -> bool:
        """
        Check for existing master password or create a new one, then authenticate.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        self._ensure_secure_folder()
        
        if not os.path.exists(self.master_file):
            print("🆕 Welcome to Password Manager!")
            print("No master password found. Let's create one.")
            print()
            
            if not self._create_master_password():
                return False
            
            print("\nNow let's verify your new password:")
            return self._verify_master_password()
        else:
            return self._verify_master_password()
    
    def change_master_password(self, current_password: str, new_password: str) -> bool:
        """
        Change the master password (for programmatic use).
        
        Args:
            current_password (str): Current master password
            new_password (str): New master password
            
        Returns:
            bool: True if password changed successfully, False otherwise
        """
        if not os.path.exists(self.master_file):
            return False
        
        try:
            # Verify current password
            with open(self.master_file, "rb") as f:
                stored_hash = f.read()
            
            if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
                return False
            
            # Create new hash
            salt = bcrypt.gensalt(rounds=12)
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            # Save new password
            with open(self.master_file, "wb") as f:
                f.write(new_hash)
            
            return True
            
        except Exception:
            return False

# Global instance for backward compatibility
_auth_manager = AuthenticationManager()

# Legacy function for backward compatibility
def check_or_create_master_password() -> bool:
    """Check or create master password (legacy function)."""
    return _auth_manager.check_or_create_master_password()