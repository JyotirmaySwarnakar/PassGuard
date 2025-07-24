#!/usr/bin/env python3
"""
JSON Import/Export Module
Handles encrypted JSON backup and restore with duplicate detection and handling.
"""

import json
import os
from typing import List, Dict, Any
from .db import get_credentials, add_credential, _db_manager
from .crypto_utils import get_fernet

class ImportResult:
    """Container for import operation results."""
    def __init__(self):
        self.imported = 0
        self.skipped = 0
        self.updated = 0
        self.errors = 0
        self.error_details = []

def export_credentials_json(filepath: str) -> bool:
    """
    Export all credentials to encrypted JSON file.
    
    Args:
        filepath (str): Output file path
        
    Returns:
        bool: True if export successful, False otherwise
    """
    # Validate filepath
    if not filepath or filepath.isspace():
        print("❌ Please provide a valid file path.")
        return False
    
    filepath = filepath.strip()
    
    # Check if it's a directory
    if os.path.isdir(filepath):
        print("❌ Please provide a full file path, not a directory.")
        return False
    
    # Check if directory exists
    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
    
    try:
        # Get all credentials
        creds = get_credentials()
        
        if not creds:
            print("📝 No credentials to export.")
            return True
        
        # Prepare data for export
        export_data = {
            "version": "1.0",
            "credentials": [
                {
                    "service": service,
                    "username": username,
                    "password": password
                }
                for service, username, password in creds
            ]
        }
        
        # Encrypt the data
        fernet = get_fernet()
        json_data = json.dumps(export_data, indent=2)
        encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
        
        # Write to file
        with open(filepath, "wb") as f:
            f.write(encrypted_data)
        
        print(f"✅ Exported {len(creds)} credential(s) to '{filepath}' (encrypted)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to export credentials: {e}")
        return False

def import_credentials_json(filepath: str) -> ImportResult:
    """
    Import credentials from encrypted JSON file with duplicate handling.
    
    Args:
        filepath (str): Input file path
        
    Returns:
        ImportResult: Detailed results of the import operation
    """
    result = ImportResult()
    
    # Validate filepath
    if not filepath or filepath.isspace():
        print("❌ Please provide a valid file path.")
        return result
    
    filepath = filepath.strip()
    
    # Check if it's a directory
    if os.path.isdir(filepath):
        print("❌ Please provide a full file path, not a directory.")
        return result
    
    # Check if file exists
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return result
    
    try:
        # Read and decrypt file
        with open(filepath, "rb") as f:
            encrypted_data = f.read()
        
        fernet = get_fernet()
        json_data = fernet.decrypt(encrypted_data).decode('utf-8')
        data = json.loads(json_data)
        
        # Validate data structure
        if not isinstance(data, dict) or 'credentials' not in data:
            print("❌ Invalid backup file format.")
            return result
        
        credentials_list = data['credentials']
        if not isinstance(credentials_list, list):
            print("❌ Invalid credentials data in backup file.")
            return result
        
        if not credentials_list:
            print("📝 No credentials found in backup file.")
            return result
        
        # Analyze for duplicates
        print(f"🔍 Analyzing {len(credentials_list)} credential(s) for duplicates...")
        analysis = _db_manager.get_duplicate_analysis(credentials_list)
        
        new_credentials = analysis['new']
        duplicate_credentials = analysis['duplicates']
        
        print(f"📊 Analysis complete:")
        print(f"   - New credentials: {len(new_credentials)}")
        print(f"   - Duplicate credentials: {len(duplicate_credentials)}")
        
        # Import new credentials first
        for cred in new_credentials:
            try:
                add_credential(cred['service'], cred['username'], cred['password'])
                result.imported += 1
            except Exception as e:
                result.errors += 1
                result.error_details.append(f"Failed to import {cred['service']}: {e}")
        
        if new_credentials:
            print(f"✅ Imported {len(new_credentials)} new credential(s)")
        
        # Handle duplicates if any exist
        if duplicate_credentials:
            print(f"\n⚠️  Found {len(duplicate_credentials)} duplicate credential(s):")
            print("-" * 60)
            
            for i, dup in enumerate(duplicate_credentials, 1):
                print(f"{i:2d}. {dup['service']} | {dup['username']}")
                if dup['passwords_match']:
                    print(f"    Status: Identical (same password)")
                else:
                    print(f"    Status: Different password")
            
            print("-" * 60)
            print("\nOptions for handling duplicates:")
            print("  1. Skip all duplicates")
            print("  2. Replace all duplicates")
            print("  3. Handle each duplicate individually")
            print("  4. Cancel duplicate import")
            
            while True:
                choice = input("\nSelect option (1-4): ").strip()
                
                if choice == '1':
                    # Skip all duplicates
                    result.skipped = len(duplicate_credentials)
                    print(f"⏭️  Skipped {result.skipped} duplicate credential(s)")
                    break
                
                elif choice == '2':
                    # Replace all duplicates
                    for dup in duplicate_credentials:
                        try:
                            _db_manager.update_credential(
                                dup['service'], 
                                dup['username'], 
                                dup['new_password']
                            )
                            result.updated += 1
                        except Exception as e:
                            result.errors += 1
                            result.error_details.append(f"Failed to update {dup['service']}: {e}")
                    
                    print(f"🔄 Updated {result.updated} duplicate credential(s)")
                    break
                
                elif choice == '3':
                    # Handle individually
                    for dup in duplicate_credentials:
                        print(f"\n📋 Duplicate found:")
                        print(f"   Service: {dup['service']}")
                        print(f"   Username: {dup['username']}")
                        print(f"   Passwords match: {'Yes' if dup['passwords_match'] else 'No'}")
                        
                        while True:
                            action = input("   Action - (s)kip, (r)eplace, (q)uit handling: ").strip().lower()
                            
                            if action == 's':
                                result.skipped += 1
                                print("   ⏭️  Skipped")
                                break
                            elif action == 'r':
                                try:
                                    _db_manager.update_credential(
                                        dup['service'], 
                                        dup['username'], 
                                        dup['new_password']
                                    )
                                    result.updated += 1
                                    print("   🔄 Updated")
                                except Exception as e:
                                    result.errors += 1
                                    result.error_details.append(f"Failed to update {dup['service']}: {e}")
                                    print(f"   ❌ Update failed: {e}")
                                break
                            elif action == 'q':
                                # Skip remaining duplicates
                                remaining = len(duplicate_credentials) - (result.skipped + result.updated + result.errors)
                                result.skipped += remaining
                                print(f"   ⏭️  Skipped remaining {remaining} duplicate(s)")
                                break
                            else:
                                print("   Invalid option. Please enter 's', 'r', or 'q'.")
                        
                        if action == 'q':
                            break
                    break
                
                elif choice == '4':
                    # Cancel duplicate import
                    result.skipped = len(duplicate_credentials)
                    print("❌ Cancelled duplicate import")
                    break
                
                else:
                    print("Invalid option. Please enter 1, 2, 3, or 4.")
        
        # Print final summary
        print(f"\n📈 Import Summary:")
        print(f"   ✅ New credentials imported: {result.imported}")
        print(f"   🔄 Credentials updated: {result.updated}")
        print(f"   ⏭️  Credentials skipped: {result.skipped}")
        print(f"   ❌ Errors: {result.errors}")
        
        if result.error_details:
            print(f"\n🚨 Error Details:")
            for error in result.error_details:
                print(f"   - {error}")
        
        return result
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in backup file.")
        return result
    except Exception as e:
        print(f"❌ Failed to import credentials: {e}")
        return result

# Legacy function for backward compatibility
def import_credentials_json_legacy(filepath: str):
    """Legacy import function for backward compatibility."""
    result = import_credentials_json(filepath)
    if result.imported > 0 or result.updated > 0:
        total_processed = result.imported + result.updated
        print(f"[✓] Processed {total_processed} credentials from {filepath}")
    elif result.errors > 0:
        print(f"[✗] Import failed with {result.errors} errors")
    else:
        print(f"[!] No credentials were imported from {filepath}")

# Maintain backward compatibility
def export_credentials_json_legacy(filepath: str):
    """Legacy export function for backward compatibility."""
    export_credentials_json(filepath)