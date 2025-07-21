# main.py

import os
import getpass
from modules.config import MASTER_PASSWORD_FILE, SECURE_FOLDER
from modules.auth import check_or_create_master_password
from modules.db import initialize_db, add_credential, get_credentials
from modules.session import SessionManager
from modules.clipboard_utils import copy_to_clipboard

def main():
    # Create the secure folder if it doesn't exist
    os.makedirs(SECURE_FOLDER, exist_ok=True)

    # Step 1: Authenticate user
    if not check_or_create_master_password():
        return  # Exit if auth fails

    # Step 2: Initialize the encrypted database
    initialize_db()

    # Step 3: Start session manager
    session = SessionManager(timeout_seconds=300)  # 5 minutes session timeout
    session.refresh()

    # Step 4: Menu loop
    while True:
        if session.is_locked():
            print("Session timed out. Please log in again.")
            if not check_or_create_master_password():
                print("Exiting for security.")
                break
            session.refresh()
            continue

        print("\n==== Local Password Manager ====")
        print("1. Add credential")
        print("2. View credentials")
        print("3. Exit")

        choice = input("Select an option: ").strip()
        session.refresh()  # Reset session timer on every action

        if choice == "1":
            service = input("🔹 Service Name: ").strip()
            username = input("👤 Username: ").strip()
            password = getpass.getpass("🔑 Password: ").strip()  # hidden input
            add_credential(service, username, password)
            print("[✓] Credential saved securely.")

        elif choice == "2":
            print("\n🔐 Saved Credentials:")
            credentials = get_credentials()
            for idx, (service, username, password) in enumerate(credentials, 1):
                print(f"{idx}. {service} - {username} - [Hidden]")
            if credentials:
                try:
                    sel = int(input("Enter the number of the credential to copy password (or 0 to skip): "))
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
