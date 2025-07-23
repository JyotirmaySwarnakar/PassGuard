# main.py

import os
import getpass
import signal
from modules.config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from modules.auth import check_or_create_master_password
from modules.db import initialize_db, add_credential, get_credentials, edit_credential, remove_credential
from modules.session import SessionManager
from modules.clipboard_utils import copy_to_clipboard
from modules.json_io import export_credentials_json, import_credentials_json

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def timed_input(prompt, timeout):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        value = input(prompt)
        signal.alarm(0)
        return value
    except TimeoutException:
        return None
    finally:
        signal.alarm(0)

def timed_getpass(prompt, timeout):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        value = getpass.getpass(prompt)
        signal.alarm(0)
        return value
    except TimeoutException:
        return None
    finally:
        signal.alarm(0)

def clear_screen():
    os.system("clear")

def filter_credentials(credentials, query):
    if not query:
        return credentials
    query = query.lower()
    return [
        (service, username, password)
        for (service, username, password) in credentials
        if query in service.lower()
    ]

def main():
    os.makedirs(SECURE_FOLDER, exist_ok=True)

    if not check_or_create_master_password():
        return

    initialize_db()

    session = SessionManager(timeout_seconds=180)  # 3 minutes
    session.refresh()

    while True:
        if session.is_locked():
            clear_screen()
            print("[SessionManager] Session timed out. Please re-authenticate.\n")
            if not check_or_create_master_password():
                print("Exiting for security.")
                break
            session.refresh()
            continue

        print("\n==== Local Password Manager ====")
        print("1. View credentials")
        print("2. Add credential")
        print("3. Export credentials (JSON, encrypted)")
        print("4. Import credentials (JSON, encrypted)")
        print("5. Settings")
        print("6. Exit")

        choice = timed_input("Select an option: ", session.timeout)
        if choice is None:
            session.lock()
            continue
        session.refresh()

        if choice == "1":
            while True:
                all_credentials = get_credentials()
                if not all_credentials:
                    print("No credentials stored yet.")
                    break

                search_query = timed_input("Search for service (Hit ENTER for view all): ", session.timeout)
                if search_query is None:
                    session.lock()
                    break
                filtered_credentials = filter_credentials(all_credentials, search_query.strip())
                if not filtered_credentials:
                    print("No matching credentials found.")
                    continue

                print("\n🔐 Matching Credentials:")
                for idx, (service, username, _) in enumerate(filtered_credentials, 1):
                    print(f"{idx}. {service} - {username}")
                print("\nOptions:")
                print("0. Copy password")
                print("1. Edit credential")
                print("2. Remove credential")
                print("3. Back to main menu")
                sub_choice = timed_input("Choose an option: ", session.timeout)
                if sub_choice is None:
                    session.lock()
                    break
                if sub_choice == "3":
                    break
                elif sub_choice == "0":
                    sel = timed_input("Enter the number of the credential to copy password: ", session.timeout)
                    if sel is None:
                        session.lock()
                        break
                    try:
                        sel = int(sel)
                        if 1 <= sel <= len(filtered_credentials):
                            _, _, password = filtered_credentials[sel - 1]
                            copy_to_clipboard(password)
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input.")
                elif sub_choice == "1":
                    sel = timed_input("Enter the number of the credential to edit: ", session.timeout)
                    if sel is None:
                        session.lock()
                        break
                    try:
                        sel = int(sel)
                        if 1 <= sel <= len(filtered_credentials):
                            # Find the index in the full credentials list
                            cred = filtered_credentials[sel - 1]
                            idx_in_all = all_credentials.index(cred)
                            old_service, old_username, old_password = cred
                            print(f"Editing credential #{sel}:")
                            print(f"Service Name [Hit Enter to keep original \"{old_service}\" ]: ", end="")
                            new_service = timed_input("", session.timeout)
                            if new_service is None:
                                session.lock()
                                break
                            new_service = new_service.strip() or old_service
                            print(f"Username [Hit Enter to keep orginal \"{old_username}\" ]: ", end="")
                            new_username = timed_input("", session.timeout)
                            if new_username is None:
                                session.lock()
                                break
                            new_username = new_username.strip() or old_username
                            print(f"Password [Hit Enter to keep original]: ", end="")
                            new_password = timed_getpass("Password [Hit Enter to keep original]: ", session.timeout)
                            if new_password is None:
                                session.lock()
                                break
                            new_password = new_password.strip() or old_password
                            if not new_service.strip() or not new_username.strip() or not new_password.strip():
                                print("❌ Service, username, and password cannot be empty.")
                                continue
                            confirm = timed_input("Press ENTER to confirm update, or Ctrl+C to cancel: ", session.timeout)
                            if confirm is None:
                                session.lock()
                                break
                            edit_credential(idx_in_all + 1, new_service, new_username, new_password)
                            print("[✓] Credential updated.")
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input.")
                    except IndexError as e:
                        print(f"❌ {e}")
                elif sub_choice == "2":
                    sel = timed_input("Enter the number of the credential to remove: ", session.timeout)
                    if sel is None:
                        session.lock()
                        break
                    try:
                        sel = int(sel)
                        if 1 <= sel <= len(filtered_credentials):
                            cred = filtered_credentials[sel - 1]
                            idx_in_all = all_credentials.index(cred)
                            confirm = timed_input("Press ENTER to confirm deletion, or Ctrl+C to cancel: ", session.timeout)
                            if confirm is None:
                                session.lock()
                                break
                            remove_credential(idx_in_all + 1)
                            print("[✓] Credential removed.")
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input.")
                    except IndexError as e:
                        print(f"❌ {e}")
                else:
                    print("Invalid option. Please try again.")

        elif choice == "2":
            service = timed_input("🔹 Service Name: ", session.timeout)
            if service is None:
                session.lock()
                continue
            username = timed_input("👤 Username: ", session.timeout)
            if username is None:
                session.lock()
                continue
            password = timed_getpass("🔑 Password: ", session.timeout)
            if password is None:
                session.lock()
                continue
            if not service.strip() or not username.strip() or not password.strip():
                print("❌ Service, username, and password cannot be empty.")
                continue
            confirm = timed_input("Are you sure you want to save this credential? (y/n): ", session.timeout)
            if confirm is None or confirm.lower() != "y":
                print("Cancelled.")
                continue
            try:
                add_credential(service, username, password)
                print("[✓] Credential saved securely.")
            except ValueError as ve:
                print(f"❌ {ve}")

        elif choice == "3":
            path = timed_input("Export file path: ", session.timeout)
            if path:
                export_credentials_json(path.strip())
        elif choice == "4":
            path = timed_input("Import file path: ", session.timeout)
            if path:
                import_credentials_json(path.strip())
        elif choice == "5":
            while True:
                print("\n--- Settings ---")
                print("1. Change session timeout")
                print("2. Change master password")
                print("3. Back to main menu")
                setting_choice = timed_input("Select an option: ", session.timeout)
                if setting_choice is None or setting_choice == "3":
                    break
                elif setting_choice == "1":
                    new_timeout = timed_input("Enter new session timeout in seconds (current: {}): ".format(session.timeout), session.timeout)
                    if new_timeout is None:
                        print("Cancelled.")
                        continue
                    try:
                        new_timeout = int(new_timeout)
                        if new_timeout < 30 or new_timeout > 3600:
                            print("❌ Timeout must be between 30 and 3600 seconds.")
                            continue
                        session.timeout = new_timeout
                        session.refresh()
                        print(f"[✓] Session timeout updated to {new_timeout} seconds.")
                    except ValueError:
                        print("❌ Invalid input. Please enter a number.")
                elif setting_choice == "2":
                    print("Change master password:")
                    from modules.auth import MASTER_PASSWORD_FILE
                    import bcrypt
                    import getpass
                    # Authenticate old password
                    with open(MASTER_PASSWORD_FILE, "rb") as f:
                        stored_hash = f.read()
                    for _ in range(3):
                        old_pw = getpass.getpass("Enter current master password: ")
                        if bcrypt.checkpw(old_pw.encode(), stored_hash):
                            break
                        else:
                            print("❌ Incorrect password.")
                    else:
                        print("❌ Too many failed attempts.")
                        continue
                    # Set new password
                    while True:
                        new_pw = getpass.getpass("Enter new master password: ")
                        confirm_pw = getpass.getpass("Confirm new master password: ")
                        if new_pw == confirm_pw:
                            break
                        print("Passwords do not match. Try again.")
                    hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
                    with open(MASTER_PASSWORD_FILE, "wb") as f:
                        f.write(hashed)
                    print("[✓] Master password changed.")
                else:
                    print("Invalid option. Please try again.")

        elif choice == "6":
            print("Goodbye!")
            session.stop()
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
