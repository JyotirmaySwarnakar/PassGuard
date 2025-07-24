#!/usr/bin/env python3
"""
Local Password Manager - Secure CLI Password Storage
A secure, lightweight command-line password manager with AES-256 encryption and 2FA support.
"""

import os
import sys
import getpass
import signal
from modules.config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from modules.auth import check_or_create_master_password
from modules.db import initialize_db, add_credential, get_credentials, edit_credential, remove_credential
from modules.session import SessionManager
from modules.clipboard_utils import copy_to_clipboard
from modules.json_io import export_credentials_json, import_credentials_json
from modules.totp_utils import get_or_create_totp_secret, verify_totp, is_totp_enabled, enable_totp, disable_totp
from modules.utils import load_session_timeout, save_session_timeout

class TimeoutException(Exception):
    """Raised when input times out"""
    pass

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    raise TimeoutException

def timed_input(prompt, timeout):
    """Get user input with timeout"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        value = input(prompt)
        signal.alarm(0)
        return value
    except TimeoutException:
        print("\n⏰ Session timed out.")
        return None
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled.")
        signal.alarm(0)
        return None
    finally:
        signal.alarm(0)

def timed_getpass(prompt, timeout):
    """Get password input with timeout"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        value = getpass.getpass(prompt)
        signal.alarm(0)
        return value
    except TimeoutException:
        print("\n⏰ Session timed out.")
        return None
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled.")
        signal.alarm(0)
        return None
    finally:
        signal.alarm(0)

def clear_screen():
    """Clear terminal screen"""
    os.system("clear" if os.name != "nt" else "cls")

def filter_credentials(credentials, query):
    """Filter credentials by service name"""
    if not query:
        return credentials
    query = query.lower()
    return [
        (service, username, password)
        for (service, username, password) in credentials
        if query in service.lower() or query in username.lower()
    ]

def print_banner():
    """Print application banner"""
    banner = """
╔════════════════════════════════════╗
║           🔐 PassGrard             ║
║     Secure • Local • Private       ║
╚════════════════════════════════════╝
"""
    print(banner)

def confirm_action(message, session):
    """Get user confirmation for sensitive actions"""
    response = timed_input(f"{message} (y/N): ", session.timeout)
    return response and response.lower() == 'y'

def handle_view_credentials(session):
    """Handle viewing and managing credentials"""
    while True:
        all_credentials = get_credentials()
        if not all_credentials:
            print("📝 No credentials stored yet.")
            print("💡 Use option 2 from the main menu to add your first credential.")
            break

        search_query = timed_input("🔍 Search for service (Enter for all): ", session.timeout)
        if search_query is None:
            session.lock()
            break
            
        session.refresh()
        filtered_credentials = filter_credentials(all_credentials, search_query.strip())
        
        if not filtered_credentials:
            print("❌ No matching credentials found.")
            continue

        print(f"\n🔐 Found {len(filtered_credentials)} credential(s):")
        print("-" * 50)
        for idx, (service, username, _) in enumerate(filtered_credentials, 1):
            print(f"{idx:2d}. {service:<20} | {username}")
        print("-" * 50)
        
        print("\nActions:")
        print("  c) Copy password to clipboard")
        print("  e) Edit credential")
        print("  d) Delete credential")
        print("  b) Back to main menu")
        
        action = timed_input("Choose action: ", session.timeout)
        if action is None:
            session.lock()
            break
        if action.lower() == 'b':
            break
            
        session.refresh()
        
        if action.lower() == 'c':
            handle_copy_password(filtered_credentials, session)
        elif action.lower() == 'e':
            handle_edit_credential(filtered_credentials, all_credentials, session)
        elif action.lower() == 'd':
            handle_delete_credential(filtered_credentials, all_credentials, session)
        else:
            print("❌ Invalid option.")

def handle_copy_password(filtered_credentials, session):
    """Handle copying password to clipboard"""
    sel = timed_input("Enter credential number: ", session.timeout)
    if sel is None:
        session.lock()
        return
    
    try:
        sel = int(sel)
        if 1 <= sel <= len(filtered_credentials):
            _, _, password = filtered_credentials[sel - 1]
            copy_to_clipboard(password)
            print("✅ Password copied to clipboard!")
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Please enter a valid number.")

def handle_edit_credential(filtered_credentials, all_credentials, session):
    """Handle editing a credential"""
    sel = timed_input("Enter credential number to edit: ", session.timeout)
    if sel is None:
        session.lock()
        return
    
    try:
        sel = int(sel)
        if 1 <= sel <= len(filtered_credentials):
            cred = filtered_credentials[sel - 1]
            idx_in_all = all_credentials.index(cred) + 1
            old_service, old_username, old_password = cred
            
            print(f"\nEditing: {old_service} | {old_username}")
            print("(Press Enter to keep current value)")
            
            new_service = timed_input(f"Service [{old_service}]: ", session.timeout)
            if new_service is None:
                session.lock()
                return
            new_service = new_service.strip() or old_service
            
            new_username = timed_input(f"Username [{old_username}]: ", session.timeout)
            if new_username is None:
                session.lock()
                return
            new_username = new_username.strip() or old_username
            
            new_password = timed_getpass("New password (Enter to keep current): ", session.timeout)
            if new_password is None:
                session.lock()
                return
            new_password = new_password.strip() or old_password
            
            if confirm_action("💾 Save changes?", session):
                edit_credential(idx_in_all, new_service, new_username, new_password)
                print("✅ Credential updated successfully!")
            else:
                print("❌ Changes cancelled.")
        else:
            print("❌ Invalid selection.")
    except (ValueError, IndexError) as e:
        print(f"❌ Error: {e}")

def handle_delete_credential(filtered_credentials, all_credentials, session):
    """Handle deleting a credential"""
    sel = timed_input("Enter credential number to delete: ", session.timeout)
    if sel is None:
        session.lock()
        return
    
    try:
        sel = int(sel)
        if 1 <= sel <= len(filtered_credentials):
            cred = filtered_credentials[sel - 1]
            idx_in_all = all_credentials.index(cred) + 1
            service, username, _ = cred
            
            print(f"⚠️  Delete: {service} | {username}")
            if confirm_action("🗑️  This action cannot be undone. Continue?", session):
                remove_credential(idx_in_all)
                print("✅ Credential deleted successfully!")
            else:
                print("❌ Deletion cancelled.")
        else:
            print("❌ Invalid selection.")
    except (ValueError, IndexError) as e:
        print(f"❌ Error: {e}")

def handle_add_credential(session):
    """Handle adding a new credential"""
    print("\n➕ Add New Credential")
    print("-" * 25)
    
    service = timed_input("🔹 Service name: ", session.timeout)
    if service is None:
        session.lock()
        return
    
    username = timed_input("👤 Username/Email: ", session.timeout)
    if username is None:
        session.lock()
        return
    
    password = timed_getpass("🔑 Password: ", session.timeout)
    if password is None:
        session.lock()
        return
    
    if not all([service.strip(), username.strip(), password.strip()]):
        print("❌ All fields are required.")
        return
    
    print(f"\nService: {service}")
    print(f"Username: {username}")
    print("Password: [hidden]")
    
    if confirm_action("💾 Save this credential?", session):
        try:
            add_credential(service.strip(), username.strip(), password.strip())
            print("✅ Credential saved securely!")
        except ValueError as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Credential not saved.")

def handle_import_export(session):
    """Handle import/export operations"""
    while True:
        print("\n📤 Import/Export Credentials")
        print("-" * 30)
        print("1. Export credentials (encrypted backup)")
        print("2. Import credentials (restore from backup)")
        print("3. Back to main menu")
        
        choice = timed_input("Select option: ", session.timeout)
        if choice is None or choice == "3":
            break
        
        session.refresh()
        
        if choice == "1":
            path = timed_input("Export file path: ", session.timeout)
            if path and path.strip():
                export_credentials_json(path.strip())
        elif choice == "2":
            path = timed_input("Import file path: ", session.timeout)
            if path and path.strip():
                import_credentials_json(path.strip())
        else:
            print("❌ Invalid option.")

def handle_settings(session):
    """Handle application settings"""
    while True:
        print("\n⚙️  Settings")
        print("-" * 15)
        print("1. Change session timeout")
        print("2. Change master password")
        print("3. Two-factor authentication")
        print("4. Back to main menu")
        
        choice = timed_input("Select option: ", session.timeout)
        if choice is None or choice == "4":
            break
        
        session.refresh()
        
        if choice == "1":
            handle_timeout_settings(session)
        elif choice == "2":
            handle_master_password_change(session)
        elif choice == "3":
            handle_2fa_settings(session)
        else:
            print("❌ Invalid option.")

def handle_timeout_settings(session):
    """Handle session timeout settings"""
    current_timeout = session.timeout
    print(f"\nCurrent timeout: {current_timeout} seconds ({current_timeout//60}:{current_timeout%60:02d})")
    
    new_timeout = timed_input("New timeout (30-3600 seconds): ", session.timeout)
    if new_timeout is None:
        session.lock()
        return
    
    try:
        new_timeout = int(new_timeout)
        if 30 <= new_timeout <= 3600:
            session.timeout = new_timeout
            session.refresh()
            save_session_timeout(new_timeout)
            print(f"✅ Timeout updated to {new_timeout} seconds!")
        else:
            print("❌ Timeout must be between 30 and 3600 seconds.")
    except ValueError:
        print("❌ Please enter a valid number.")

def handle_master_password_change(session):
    """Handle master password change"""
    print("\n🔑 Change Master Password")
    print("-" * 25)
    
    # Verify current password
    import bcrypt
    with open(MASTER_PASSWORD_FILE, "rb") as f:
        stored_hash = f.read()
    
    for attempt in range(3):
        current_pw = getpass.getpass("Current master password: ")
        if bcrypt.checkpw(current_pw.encode(), stored_hash):
            break
        print(f"❌ Incorrect password. {2-attempt} attempts remaining.")
    else:
        print("❌ Too many failed attempts.")
        return
    
    # 2FA verification if enabled
    if is_totp_enabled():
        print("🔒 2FA verification required.")
        for attempt in range(3):
            code = timed_input("Enter 2FA code: ", session.timeout)
            if code and verify_totp(code):
                print("✅ 2FA verified.")
                break
            print(f"❌ Invalid 2FA code. {2-attempt} attempts remaining.")
        else:
            print("❌ Too many failed 2FA attempts.")
            return
    
    # Set new password
    while True:
        new_pw = getpass.getpass("New master password: ")
        confirm_pw = getpass.getpass("Confirm new password: ")
        if new_pw == confirm_pw:
            if len(new_pw) >= 8:
                break
            else:
                print("❌ Password must be at least 8 characters long.")
        else:
            print("❌ Passwords don't match. Try again.")
    
    # Save new password
    hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
    with open(MASTER_PASSWORD_FILE, "wb") as f:
        f.write(hashed)
    print("✅ Master password changed successfully!")

def handle_2fa_settings(session):
    """Handle 2FA settings"""
    while True:
        enabled = is_totp_enabled()
        status = "✅ Enabled" if enabled else "❌ Disabled"
        
        print(f"\n🔐 Two-Factor Authentication - {status}")
        print("-" * 35)
        print("1. Enable 2FA")
        print("2. Disable 2FA")
        print("3. Show QR secret")
        print("4. Back to settings")
        
        choice = timed_input("Select option: ", session.timeout)
        if choice is None or choice == "4":
            break
        
        session.refresh()
        
        if choice == "1":
            if not enabled:
                enable_totp()
            else:
                print("ℹ️  2FA is already enabled.")
        elif choice == "2":
            if enabled:
                if verify_2fa_for_disable(session):
                    disable_totp()
            else:
                print("ℹ️  2FA is not enabled.")
        elif choice == "3":
            if verify_master_password():
                secret = get_or_create_totp_secret()
                print(f"\n📱 TOTP Secret (scan with authenticator app):")
                print(f"🔑 {secret}")
                print("\n💡 Compatible apps: Google Authenticator, Authy, 1Password")
        else:
            print("❌ Invalid option.")

def verify_2fa_for_disable(session):
    """Verify 2FA before disabling"""
    print("🔒 2FA verification required to disable.")
    for attempt in range(3):
        code = timed_input("Enter 2FA code: ", session.timeout)
        if code and verify_totp(code):
            return True
        print(f"❌ Invalid code. {2-attempt} attempts remaining.")
    print("❌ Too many failed attempts.")
    return False

def verify_master_password():
    """Verify master password"""
    import bcrypt
    with open(MASTER_PASSWORD_FILE, "rb") as f:
        stored_hash = f.read()
    
    for attempt in range(3):
        password = getpass.getpass("Enter master password: ")
        if bcrypt.checkpw(password.encode(), stored_hash):
            return True
        print(f"❌ Incorrect password. {2-attempt} attempts remaining.")
    print("❌ Too many failed attempts.")
    return False

def main():
    """Main application entry point"""
    try:
        # Setup
        clear_screen()
        print_banner()
        
        # Initialize secure folder and database
        os.makedirs(SECURE_FOLDER, exist_ok=True)
        if not check_or_create_master_password():
            print("👋 Goodbye!")
            return
        
        initialize_db()
        
        # Session management
        session_timeout = load_session_timeout(default=180)
        session = SessionManager(timeout_seconds=session_timeout)
        session.refresh()
        
        print("✅ Authentication successful!")
        print(f"⏰ Session timeout: {session_timeout//60}:{session_timeout%60:02d}")
        
        # Main application loop
        while True:
            # Check session
            if session.is_locked():
                clear_screen()
                print("🔒 Session expired. Please re-authenticate.")
                if not check_or_create_master_password():
                    print("👋 Goodbye!")
                    break
                session.refresh()
                continue
            
            # Main menu
            print("\n" + "="*45)
            print("🔐 PassGuard")
            print("="*45)
            print("1. 👀 View & manage credentials")
            print("2. ➕ Add new credential")
            print("3. 📤 Import/Export")
            print("4. ⚙️  Settings")
            print("5. 🚪 Exit")
            print("-"*45)
            
            choice = timed_input("Select option (1-5): ", session.timeout)
            if choice is None:
                session.lock()
                continue
            
            session.refresh()
            
            # Handle menu choices
            if choice == "1":
                handle_view_credentials(session)
            elif choice == "2":
                handle_add_credential(session)
            elif choice == "3":
                handle_import_export(session)
            elif choice == "4":
                handle_settings(session)
            elif choice == "5":
                print("\n👋 Thank you for using PassGuard")
                print("🔒 Your data remains secure and encrypted.")
                session.stop()
                break
            else:
                print("❌ Invalid option. Please select 1-5.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting securely...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🔒 Your data remains secure. Please restart the application.")
        sys.exit(1)

if __name__ == "__main__":
    main()