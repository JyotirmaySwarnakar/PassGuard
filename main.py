# main.py

import os
import getpass
import signal
from modules.config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from modules.auth import check_or_create_master_password
from modules.db import initialize_db, add_credential, get_credentials
from modules.session import SessionManager
from modules.clipboard_utils import copy_to_clipboard

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
        # Do not print here, let main handle the message
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
        # Do not print here, let main handle the message
        return None
    finally:
        signal.alarm(0)

def clear_screen():
    os.system("clear")

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
        print("1. Add credential")
        print("2. View credentials")
        print("3. Exit")

        choice = timed_input("Select an option: ", session.timeout)
        if choice is None:
            session.lock()
            continue
        session.refresh()

        if choice == "1":
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
            add_credential(service, username, password)
            print("[✓] Credential saved securely.")

        elif choice == "2":
            print("\n🔐 Saved Credentials:")
            credentials = get_credentials()
            for idx, (service, username, password) in enumerate(credentials, 1):
                print(f"{idx}. {service} - {username} - [Hidden]")
            if credentials:
                sel = timed_input("Enter the number of the credential to copy password (or 0 to skip): ", session.timeout)
                if sel is None:
                    session.lock()
                    continue
                try:
                    sel = int(sel)
                    if 1 <= sel <= len(credentials):
                        _, _, password = credentials[sel - 1]
                        copy_to_clipboard(password)
                    elif sel == 0:
                        pass
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("No credentials stored yet.")

        elif choice == "3":
            print("Goodbye!")
            session.stop()
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
