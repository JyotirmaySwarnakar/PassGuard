# 🔐PassGuard :  Local Password Manager

A secure, lightweight command-line password manager with advanced encryption and 2FA support. Store and manage your passwords locally with military-grade security.

## ✨ Features

- **🛡️ Military-Grade Security**: AES-256 encryption with Fernet
- **🔑 Master Password Protection**: bcrypt hashed master password
- **📱 Two-Factor Authentication**: TOTP support for enhanced security
- **⏰ Session Management**: Configurable auto-lock with timeout
- **📋 Smart Clipboard**: Auto-clearing clipboard after 15 seconds
- **🔍 Search & Filter**: Quick credential lookup
- **📤 Import/Export**: Encrypted JSON backup and restore
- **🔒 Secure File Permissions**: Unix file permissions (600/700)
- **💾 Local Storage**: No cloud dependencies, full privacy control

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Unix-like system (Linux, macOS)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd password_manager
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **First-time setup**
   - Set your master password when prompted
   - Optionally enable 2FA for enhanced security

## 📁 Project Structure

```
password_manager/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                 # Git ignore rules
└── modules/
    ├── auth.py                # Authentication & master password
    ├── clipboard_utils.py     # Clipboard operations
    ├── config.py              # Configuration constants
    ├── crypto_utils.py        # Encryption/decryption utilities
    ├── db.py                  # SQLite database operations
    ├── json_io.py             # Import/export functionality
    ├── session.py             # Session management & timeouts
    ├── totp_utils.py          # Two-factor authentication
    └── utils.py               # Utility functions
```

## 🔧 Usage

### Main Menu Options

1. **View Credentials** - Browse, search, and manage stored passwords
2. **Add Credential** - Store new login credentials
3. **Import/Export** - Backup and restore encrypted credential files
4. **Settings** - Configure timeouts, 2FA, and master password
5. **Exit** - Secure application shutdown

### Managing Credentials

#### Adding a New Credential
```
🔹 Service Name: GitHub
👤 Username: your-username
🔑 Password: [hidden input]
```

#### Viewing & Searching
- Search by service name or view all credentials
- Copy passwords directly to clipboard
- Auto-clearing clipboard after 15 seconds

#### Editing Credentials
- Update service name, username, or password
- Press Enter to keep existing values unchanged

### Security Settings

#### Session Timeout
- Default: 3 minutes (180 seconds)
- Range: 30-3600 seconds
- Auto-lock on inactivity

#### Two-Factor Authentication
- Enable TOTP using any authenticator app
- Required for sensitive operations
- QR code compatible secret generation

#### Master Password
- Change master password with 2FA verification
- bcrypt hashed with salt
- 3 attempt limit before lockout

### Import/Export

#### Export Credentials
```bash
Export file path: ~/backups/passwords_backup.json
[✓] Exported 15 credentials to ~/backups/passwords_backup.json (encrypted)
```

#### Import Credentials
```bash
Import file path: ~/backups/passwords_backup.json
[✓] Imported 15 credentials from ~/backups/passwords_backup.json
```

## 🛡️ Security Architecture

### Encryption
- **Algorithm**: AES-256 with Fernet (symmetric encryption)
- **Key Generation**: Cryptographically secure random key generation
- **Password Storage**: All passwords encrypted at rest
- **Master Password**: bcrypt hashed with salt (cost factor 12)

### File Security
- **Permissions**: 700 for directories, 600 for files
- **Location**: `~/.local_passman/` (hidden directory)
- **Files**:
  - `.master` - Hashed master password
  - `.fernet_key` - Encryption key
  - `passwords.db` - Encrypted credential database
  - `.totp_secret` - 2FA secret (when enabled)

### Session Security
- **Auto-lock**: Configurable timeout (30-3600 seconds)
- **Memory Protection**: Credentials cleared from memory after use
- **Clipboard Security**: Auto-clear after 15 seconds
- **Timeout Handling**: Graceful session termination

## 📋 Requirements

Create a `requirements.txt` file with:

```
bcrypt==4.0.1
cryptography==41.0.7
pyperclip==1.8.2
pyotp==2.9.0
```

## 🔍 Troubleshooting

### Common Issues

#### "Permission denied" errors
```bash
# Fix file permissions manually
chmod 700 ~/.local_passman
chmod 600 ~/.local_passman/*
```

#### "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### Session timeout too aggressive
```bash
# Increase timeout in Settings > Change session timeout
# Recommended: 300 seconds (5 minutes) for normal use
```

#### 2FA setup issues
```bash
# Ensure authenticator app supports TOTP
# Try Google Authenticator, Authy, or 1Password
# Re-enable 2FA if having issues: Settings > 2FA settings
```

### File Locations

All application data is stored in: `~/.local_passman/`

- Remove this directory to completely reset the application
- Backup this directory to preserve all data

## 🚨 Security Best Practices

### Master Password
- Use a strong, unique master password (12+ characters)
- Include uppercase, lowercase, numbers, and symbols
- Never share or write down your master password

### 2FA Setup
- Enable 2FA for maximum security
- Use a reputable authenticator app
- Backup your 2FA secret in a secure location

### Regular Maintenance
- Export encrypted backups regularly
- Update the application and dependencies
- Review stored credentials periodically

### Physical Security
- Lock your computer when away
- Use full-disk encryption on your device
- Consider the security of your backup files

## 🔄 Backup & Recovery

### Creating Backups
1. Use the built-in export feature for encrypted backups
2. Manually copy `~/.local_passman/` directory
3. Store backups in secure, encrypted storage

### Recovery Process
1. Install the application on new system
2. Import encrypted backup file, or
3. Copy backed-up `~/.local_passman/` directory
4. Run `python main.py` and authenticate

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone <repository-url>
cd password_manager
pip install -r requirements.txt
python main.py
```

## ⚠️ Disclaimer

This password manager is designed for personal use and educational purposes. While it implements strong security practices, users should evaluate their own security requirements. The authors are not responsible for any data loss or security breaches.

## 🆘 Support

For issues, questions, or contributions:
- Open an issue on the project repository
- Review the troubleshooting section above
- Check that all dependencies are properly installed

---

**Remember**: Your security is only as strong as your weakest link. Use strong passwords, enable 2FA, and keep your system updated! 🔒