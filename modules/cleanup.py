#!/usr/bin/env python3

import os
import sys
import sqlite3
from contextlib import contextmanager
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.config import DATABASE_FILE, SECURE_FOLDER
    from modules.crypto_utils import decrypt_data
    from modules.auth import check_or_create_master_password
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

class DuplicateCleaner:
    def __init__(self):
        self.db_file = DATABASE_FILE

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def find_duplicates(self):
        duplicates = {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, service, username, password, created_at, updated_at
                    FROM credentials
                    ORDER BY service, username, updated_at DESC
                ''')
                all_credentials = cursor.fetchall()
                groups = {}
                for cred in all_credentials:
                    cred_id, service, enc_username, enc_password, created_at, updated_at = cred
                    try:
                        username = decrypt_data(enc_username)
                        password = decrypt_data(enc_password)
                    except Exception as e:
                        print(f"⚠️  Warning: Could not decrypt credential ID {cred_id}: {e}")
                        continue
                    key = f"{service.lower()}||{username.lower()}"
                    if key not in groups:
                        groups[key] = []
                    groups[key].append({
                        'id': cred_id,
                        'service': service,
                        'username': username,
                        'password': password,
                        'created_at': created_at,
                        'updated_at': updated_at
                    })
                for key, group in groups.items():
                    if len(group) > 1:
                        duplicates[key] = group
        except Exception as e:
            print(f"❌ Error finding duplicates: {e}")
            return {}
        return duplicates

    def analyze_duplicates(self, duplicates):
        total_duplicates = 0
        total_to_remove = 0
        groups_count = len(duplicates)
        for group in duplicates.values():
            total_duplicates += len(group)
            total_to_remove += len(group) - 1
        return {
            'groups_count': groups_count,
            'total_duplicates': total_duplicates,
            'total_to_remove': total_to_remove
        }

    def display_duplicates(self, duplicates):
        if not duplicates:
            print("✅ No duplicate credentials found!")
            return
        analysis = self.analyze_duplicates(duplicates)
        print(f"\n📊 Duplicate Analysis:")
        print(f"   🔍 Found {analysis['groups_count']} duplicate group(s)")
        print(f"   📝 Total duplicate credentials: {analysis['total_duplicates']}")
        print(f"   🗑️  Credentials to remove: {analysis['total_to_remove']}")
        print(f"\n🔍 Duplicate Groups:")
        print("=" * 80)
        for i, (key, group) in enumerate(duplicates.items(), 1):
            service = group[0]['service']
            username = group[0]['username']
            print(f"\n{i}. Service: {service} | Username: {username}")
            print("-" * 60)
            for j, cred in enumerate(group):
                status = "🟢 KEEP" if j == 0 else "🔴 REMOVE"
                print(f"   {status} - ID: {cred['id']}")
                print(f"        Password: {'*' * len(cred['password'])} ({len(cred['password'])} chars)")
                print(f"        Created:  {cred['created_at']}")
                print(f"        Updated:  {cred['updated_at']}")
                if j > 0:
                    match = group[0]['password'] == cred['password']
                    print(f"        Password same as kept: {'Yes' if match else 'No'}")
                print()

    def remove_duplicates(self, duplicates, confirm=True):
        if not duplicates:
            return 0
        analysis = self.analyze_duplicates(duplicates)
        if confirm:
            print(f"\n⚠️  WARNING: This will remove {analysis['total_to_remove']} duplicate credential(s)!")
            print("The most recently updated credential in each group will be kept.")
            response = input("\nContinue with removal? (yes/NO): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Operation cancelled.")
                return 0
        removed_count = 0
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for group in duplicates.values():
                    for cred in group[1:]:
                        try:
                            cursor.execute('DELETE FROM credentials WHERE id = ?', (cred['id'],))
                            removed_count += 1
                            print(f"🗑️  Removed: {cred['service']} | {cred['username']} (ID: {cred['id']})")
                        except Exception as e:
                            print(f"❌ Failed to remove credential ID {cred['id']}: {e}")
                conn.commit()
                print(f"\n✅ Successfully removed {removed_count} duplicate credential(s)!")
        except Exception as e:
            print(f"❌ Error during removal: {e}")
            return 0
        return removed_count

    def backup_before_cleanup(self):
        try:
            from modules.json_io import export_credentials_json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_before_cleanup_{timestamp}.json"
            backup_path = os.path.join(os.path.dirname(self.db_file), backup_filename)
            print(f"📦 Creating backup: {backup_path}")
            if export_credentials_json(backup_path):
                print("✅ Backup created successfully!")
                return True
            else:
                print("❌ Backup failed!")
                return False
        except Exception as e:
            print(f"❌ Backup error: {e}")
            return False

def main():
    print("🔐 PassGuard - Duplicate Credential Cleaner")
    print("=" * 50)
    if not os.path.exists(DATABASE_FILE):
        print("❌ Password manager database not found!")
        print(f"Expected location: {DATABASE_FILE}")
        sys.exit(1)
    print("🔒 Authentication required to access credential database.")
    if not check_or_create_master_password():
        print("❌ Authentication failed!")
        sys.exit(1)
    cleaner = DuplicateCleaner()
    try:
        print("\n🔍 Scanning for duplicate credentials...")
        duplicates = cleaner.find_duplicates()
        cleaner.display_duplicates(duplicates)
        if not duplicates:
            print("🎉 Your credential database is clean!")
            return
        print("\n📋 Options:")
        print("1. Remove all duplicates (keeps most recent)")
        print("2. Create backup and then remove duplicates")
        print("3. Exit without changes")
        while True:
            choice = input("\nSelect option (1-3): ").strip()
            if choice == '1':
                removed = cleaner.remove_duplicates(duplicates)
                if removed > 0:
                    print(f"\n🎉 Cleanup complete! Removed {removed} duplicate credential(s).")
                break
            elif choice == '2':
                if cleaner.backup_before_cleanup():
                    removed = cleaner.remove_duplicates(duplicates)
                    if removed > 0:
                        print(f"\n🎉 Cleanup complete! Removed {removed} duplicate credential(s).")
                        print("💡 Your backup is safe in the .PassGuard folder.")
                else:
                    print("❌ Skipping cleanup due to backup failure.")
                break
            elif choice == '3':
                print("👋 Exiting without changes.")
                break
            else:
                print("❌ Invalid option. Please select 1, 2, or 3.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
