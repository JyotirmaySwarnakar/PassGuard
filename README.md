# Password Manager

This project is a simple password manager application designed to securely store and manage user passwords. It provides functionalities for authentication, database management, cryptographic operations, and session handling.

## Project Structure

```
password_manager/
├── modules/
│   ├── auth.py          # Authentication-related functions
│   ├── db.py            # Database interactions
│   ├── crypto_utils.py   # Cryptographic utilities
│   ├── clipboard_utils.py # Clipboard operations
│   ├── session.py       # User session management
│   ├── config.py        # Configuration settings
│   └── utils.py         # Utility functions
├── main.py              # Entry point for the application
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Installation

To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage

To start the password manager, run the `main.py` file:

```
python main.py
```

Follow the prompts to set up your master password and manage your passwords securely.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.


## 🔐 Security Design - Password_Manager

- Master password is hashed using `bcrypt` and stored in a local `.master` file.
- Passwords are encrypted with AES-256 using Fernet from the `cryptography` package.
- SQLite is used to store credentials; passwords are always encrypted.
- `.master` and `passwords.db` files will have permission 600 (read/write by user only).
- Session timeout is 5 minutes of inactivity.
- Clipboard auto-clears after 15 seconds by default.
- No credentials or secrets are logged or printed.

