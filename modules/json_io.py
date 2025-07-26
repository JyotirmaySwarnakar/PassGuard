#!/usr/bin/env python3

import json
import os
from typing import List, Dict, Any
from .db import get_credentials, add_credential
from .crypto_utils import get_fernet

class ImportResult:
    def __init__(self):
        self.imported = 0
        self.errors = 0
        self.error_details = []

def export_credentials_json(filepath: str) -> bool:
    if not filepath or filepath.isspace():
        print("❌ Please provide a valid file path.")
        return False

    filepath = filepath.strip()
    if os.path.isdir(filepath):
        print("❌ Please provide a full file path, not a directory.")
        return False

    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False

    try:
        creds = get_credentials()
        if not creds:
            print("📝 No credentials to export.")
            return True

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

        fernet = get_fernet()
        json_data = json.dumps(export_data, indent=2)
        encrypted_data = fernet.encrypt(json_data.encode('utf-8'))

        with open(filepath, "wb") as f:
            f.write(encrypted_data)

        print(f"✅ Exported {len(creds)} credential(s) to '{filepath}' (encrypted)")
        return True

    except Exception as e:
        print(f"❌ Failed to export credentials: {e}")
        return False

def import_credentials_json(filepath: str) -> ImportResult:
    result = ImportResult()

    if not filepath or filepath.isspace():
        return result

    filepath = filepath.strip()
    if os.path.isdir(filepath) or not os.path.exists(filepath):
        return result

    try:
        with open(filepath, "rb") as f:
            encrypted_data = f.read()

        fernet = get_fernet()
        json_data = fernet.decrypt(encrypted_data).decode('utf-8')
        data = json.loads(json_data)

        if not isinstance(data, dict) or 'credentials' not in data:
            return result

        credentials_list = data['credentials']
        if not isinstance(credentials_list, list) or not credentials_list:
            return result

        for cred in credentials_list:
            try:
                service = cred.get('service', '').strip()
                username = cred.get('username', '').strip()
                password = cred.get('password', '').strip()

                if not all([service, username, password]):
                    result.errors += 1
                    result.error_details.append("Skipped invalid credential (empty fields)")
                    continue

                add_credential(service, username, password, allow_duplicates=True)
                result.imported += 1

            except Exception as e:
                result.errors += 1
                error_msg = f"Failed to import {cred.get('service', 'unknown')}: {e}"
                result.error_details.append(error_msg)

        print(f"\n📈 Import Summary:")
        print(f"   ✅ Credentials imported: {result.imported}")
        print(f"   ❌ Errors: {result.errors}")

        if result.error_details:
            print(f"\n🚨 Error Details:")
            for error in result.error_details:
                print(f"   - {error}")

        # ✅ Run duplicate cleanup after import
        from modules.cleanup import DuplicateCleaner
        cleaner = DuplicateCleaner()
        duplicates = cleaner.find_duplicates()

        if duplicates:
            print("\n🧹 Running duplicate cleanup after import...")
            cleaner.remove_duplicates(duplicates, confirm=True)
        else:
            print("\n✅ No duplicates found after import.")

        return result

    except json.JSONDecodeError:
        return result
    except Exception:
        return result
