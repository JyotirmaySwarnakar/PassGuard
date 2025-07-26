# 🔐 PassGuard - Secure Local Password Manager

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)
[![Security](https://img.shields.io/badge/Encryption-AES--256-green.svg)](https://cryptography.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**PassGuard** is a secure, lightweight command-line password manager designed for users who prioritize privacy and local control over their sensitive data. Built with military-grade encryption and advanced security features, PassGuard ensures your passwords remain safe and accessible only to you.

## 🌟 Project Overview

In an era where data breaches and privacy concerns are paramount, PassGuard offers a robust solution for password management without relying on cloud services. This capstone project demonstrates advanced cybersecurity principles, cryptographic implementation, and secure software development practices.

### Key Highlights
- **🛡️ Military-Grade Security**: AES-256 encryption with Fernet implementation
- **🔒 Zero-Trust Architecture**: All data encrypted at rest with no cloud dependencies
- **📱 Multi-Factor Authentication**: TOTP-based 2FA for enhanced security
- **⏱️ Smart Session Management**: Configurable auto-lock with timeout protection
- **🔍 Advanced Features**: Smart search, duplicate detection, secure clipboard handling
- **📤 Backup & Recovery**: Encrypted import/export functionality

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **Unix-like system** (Linux, macOS)
- **Terminal access** with standard Unix permissions

### Installation

#### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/JyotirmaySwarnakar/passguard.git
cd passguard

# Run the automated setup
python3 setup.py
```

#### Option 2: Manual Setup
```bash
# Clone the repository
git clone https://github.com/JyotirmaySwarnakar/passguard.git
cd passguard

# Install dependencies
pip3 install -r requirements.txt

# Set executable permissions
chmod +x main.py

# Run the application
python3 main.py
```

### First Launch
```bash
python3 main.py
```

On first launch, you'll be guided through:
1. **Master Password Creation** - Set your primary authentication credential
2. **Security Settings** - Configure session timeout and optional 2FA
3. **Database Initialization** - Secure credential storage setup

---

## 🏗️ Architecture & Security

### Security Architecture

PassGuard implements a multi-layered security model:

```
┌─────────────────────────────────────────┐
│               User Input                │
├─────────────────────────────────────────┤
│          Master Password                │
│         (bcrypt hashed)                 │
├─────────────────────────────────────────┤
│         2FA Verification                │
│         (TOTP Optional)                 │
├─────────────────────────────────────────┤
│        Session Management              │
│      (Configurable Timeout)            │
├─────────────────────────────────────────┤
│       AES-256 Encryption                │
│        (Fernet Keys)                    │
├─────────────────────────────────────────┤
│       SQLite Database                   │
│     (Encrypted at Rest)                 │
├─────────────────────────────────────────┤
│      File System Security              │
│    (Unix Permissions 600/700)          │
└─────────────────────────────────────────┘
```

### Encryption Details

- **Algorithm**: AES-256 in CBC mode via Fernet (cryptographically secure)
- **Key Management**: Cryptographically secure random key generation
- **Password Hashing**: bcrypt with salt (cost factor 12)
- **Session Keys**: Memory-only storage, cleared on timeout

### File Structure
```
~/.PassGuard/                    # Secure application directory (700)
├── .master                      # Hashed master password (600)
├── .fernet_key                  # Encryption key (600)
├── passwords.db                 # Encrypted credential database (600)
├── .totp_secret                 # 2FA secret (600, optional)
└── .session_timeout            # Session configuration (600)
```

---

## ⚙️ Core Features

### 🔐 Credential Management
- **Add Credentials**: Store service name, username, and encrypted password
- **View & Search**: Quick lookup with service name filtering
- **Edit Credentials**: Update existing entries with duplicate detection
- **Delete Credentials**: Secure removal with confirmation prompts
- **Duplicate Prevention**: Automatic detection of duplicate service+username combinations

### 🛡️ Security Features
- **Master Password**: Primary authentication with strength validation
- **Two-Factor Authentication**: TOTP support compatible with Google Authenticator, Authy, 1Password
- **Session Management**: Configurable auto-lock (30-3600 seconds)
- **Secure Clipboard**: Auto-clearing clipboard after 15 seconds
- **File Permissions**: Unix permissions ensuring owner-only access

### 📊 Data Management
- **Import/Export**: Encrypted JSON backup and restore functionality
- **Duplicate Cleanup**: Built-in duplicate detection and removal tools
- **Search & Filter**: Fast credential lookup by service name or username
- **Data Integrity**: SQLite with foreign key constraints and unique indices

---

## 📖 Usage Guide

### Main Menu Navigation
```
🔐 PassGuard 
============================================
1. 👀 View & manage credentials
2. ➕ Add new credential
3. 📤 Import/Export
4. ⚙️  Settings
5. 🚪 Exit
--------------------------------------------
```

### Adding Credentials
```bash
➕ Add New Credential
-------------------------
🔹 Service name: GitHub
👤 Username/Email: user@example.com
🔑 Password: [hidden input]
🔑 Confirm password: [hidden input]

📋 Credential Summary:
   Service: GitHub
   Username: user@example.com
   Password: [hidden - 16 characters]

💾 Save this credential? (y/N): y
✅ Credential saved securely!
```

### Viewing & Managing Credentials
```bash
🔍 Search for service (Enter for all): git

🔐 Found 2 credential(s):
--------------------------------------------------
 1. GitHub               | user@example.com
 2. GitLab               | developer@company.com
--------------------------------------------------

Actions:
  c) Copy password to clipboard
  e) Edit credential
  d) Delete credential
  b) Back to main menu

Choose action: c
Enter credential number: 1
✅ Password copied to clipboard!
[Clipboard] Password copied. It will be cleared in 15 seconds.
```

### Import/Export Operations
```bash
📤 Export credentials (encrypted backup)
📁 Export file path: ~/backups/passguard_backup_2024.json
✅ Exported 25 credential(s) to '~/backups/passguard_backup_2024.json' (encrypted)

📥 Import credentials (restore from backup)  
📁 Import file path: ~/backups/passguard_backup_2024.json
✅ Successfully imported 25 credential(s)!
```

### Settings Configuration
```bash
⚙️  Settings
---------------
1. Change session timeout
2. Change master password
3. Two-factor authentication
4. Back to main menu

# Session Timeout Configuration
Current timeout: 180 seconds (3:00)
New timeout (30-3600 seconds): 300
✅ Timeout updated to 300 seconds!

# 2FA Setup
🔐 Two-Factor Authentication - ❌ Disabled
📱 TOTP Secret (scan with authenticator app):
🔑 MFRGG443FMZXG5DJMRSW45BAORSXG5A
✅ 2FA has been enabled!
```

---

## 🧪 Advanced Features

### Duplicate Cleanup Tool
PassGuard includes a built-in duplicate cleanup utility:

```bash
python3 -m modules.cleanup

🔐 PassGuard - Duplicate Credential Cleaner
==================================================
🔍 Scanning for duplicate credentials...

📊 Duplicate Analysis:
   🔍 Found 2 duplicate group(s)
   📝 Total duplicate credentials: 4
   🗑️  Credentials to remove: 2

📋 Options:
1. Remove all duplicates (keeps most recent)
2. Create backup and then remove duplicates
3. Exit without changes
```

### Session Security
- **Auto-lock**: Automatically locks after configured inactivity period
- **Timeout Handling**: Graceful session termination with data protection
- **Memory Protection**: Credentials cleared from memory after use
- **Interrupt Handling**: Secure shutdown on Ctrl+C or unexpected termination

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.7+**: Primary development language
- **SQLite3**: Embedded database for credential storage
- **cryptography**: Industry-standard encryption library
- **bcrypt**: Secure password hashing
- **pyotp**: TOTP implementation for 2FA
- **pyperclip**: Secure clipboard operations

### Dependencies
```text
bcrypt==4.0.1           # Secure password hashing
cryptography==41.0.7    # AES-256 encryption with Fernet
pyperclip==1.8.2        # Clipboard operations
pyotp==2.9.0           # TOTP 2FA implementation
```

### Development Tools
- **Setup Automation**: Automated dependency installation and configuration
- **Code Organization**: Modular architecture with clear separation of concerns
- **Error Handling**: Comprehensive exception handling and user feedback
- **Security Testing**: Built-in duplicate detection and data integrity checks

---

## 🔧 Configuration

### Environment Variables
PassGuard respects the following environment variables:

```bash
# Custom data directory (optional)
export PASSGUARD_DATA_DIR="$HOME/.config/passguard"

# Default session timeout (optional)
export PASSGUARD_DEFAULT_TIMEOUT=300
```

### File Permissions
PassGuard automatically sets secure Unix permissions:
- **Directories**: `700` (owner read/write/execute only)
- **Files**: `600` (owner read/write only)

### Platform-Specific Notes

#### Linux
- Full feature support
- Desktop entry creation available
- Shell alias integration

#### macOS
- Full feature support
- Keychain integration compatibility
- Terminal.app optimization

---

## 🚨 Security Best Practices

### For Users
1. **Strong Master Password**: Use 12+ characters with mixed case, numbers, and symbols
2. **Enable 2FA**: Add an extra layer of security for critical operations
3. **Regular Backups**: Export encrypted backups to secure storage
4. **Session Timeout**: Configure appropriate timeout for your usage pattern
5. **Physical Security**: Lock your computer when away from desk

### For Developers
1. **Code Review**: All cryptographic operations undergo security review
2. **Dependency Scanning**: Regular updates and vulnerability assessments
3. **Memory Management**: Sensitive data cleared from memory immediately after use
4. **Input Validation**: Comprehensive sanitization of all user inputs
5. **Error Handling**: No sensitive information leaked in error messages

---

## 📚 Project Structure

```
passguard/
├── main.py                     # Application entry point
├── setup.py                    # Automated installation script
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
├── LICENSE                     # MIT license
├── .gitignore                 # Git ignore rules
└── modules/                    # Core application modules
    ├── __init__.py            # Module initialization
    ├── auth.py                # Authentication & master password
    ├── clipboard_utils.py     # Clipboard operations with auto-clear
    ├── config.py              # Configuration constants & paths
    ├── crypto_utils.py        # Encryption/decryption utilities
    ├── db.py                  # SQLite database operations
    ├── json_io.py             # Import/export functionality
    ├── session.py             # Session management & timeouts
    ├── totp_utils.py          # Two-factor authentication
    ├── utils.py               # Utility functions & file permissions
    └── cleanup.py             # Duplicate detection and cleanup
```

---

## 🐛 Troubleshooting

### Common Issues

#### Installation Problems
```bash
# Permission denied errors
sudo chmod +x main.py
python3 setup.py

# Missing dependencies
pip3 install --upgrade -r requirements.txt

# Python version conflicts
python3 --version  # Ensure 3.7+
```

#### Runtime Issues
```bash
# Session timeout too aggressive
# Increase timeout in Settings > Change session timeout

# 2FA not working
# Ensure authenticator app supports TOTP
# Try disabling and re-enabling 2FA

# Database corruption
# Restore from encrypted backup using Import/Export
```

#### File Permission Issues
```bash
# Fix permissions manually
chmod 700 ~/.PassGuard
chmod 600 ~/.PassGuard/*

# Reset application data (WARNING: destroys all data)
rm -rf ~/.PassGuard
```

### Debug Mode
Enable verbose output for troubleshooting:
```bash
export PASSGUARD_DEBUG=1
python3 main.py
```

---

## 🔮 Future Enhancements

### Planned Features
- [ ] **Browser Integration**: Browser extension for seamless password filling
- [ ] **Biometric Authentication**: Fingerprint/face recognition support
- [ ] **Password Generator**: Built-in secure password generation
- [ ] **Audit Logging**: Comprehensive security event logging
- [ ] **Mobile Companion**: Secure mobile app with sync capabilities

### Contribution Opportunities
- [ ] Windows support implementation
- [ ] GUI interface development
- [ ] Additional 2FA methods (hardware keys, SMS)
- [ ] Password strength analysis
- [ ] Breach monitoring integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits & Acknowledgments

### Core Technologies
- **[Cryptography](https://cryptography.io/)** - Modern cryptographic library for Python
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Secure password hashing implementation
- **[PyOTP](https://github.com/pyotp/pyotp)** - Python One-Time Password library
- **[pyperclip](https://github.com/asweigart/pyperclip)** - Cross-platform clipboard module

### Security Inspiration
- **NIST Cybersecurity Framework** - Security architecture guidance
- **OWASP Application Security** - Security best practices implementation
- **PCI DSS Standards** - Data protection methodology

### Educational Resources
- **Cryptographic Engineering** by Niels Ferguson, Bruce Schneier, and Tadayoshi Kohno
- **Applied Cryptography** by Bruce Schneier
- **The Web Application Hacker's Handbook** by Dafydd Stuttard and Marcus Pinto

---

## 🤝 Contributing

We welcome contributions from the cybersecurity and development community!

### How to Contribute
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Include comprehensive docstrings for all functions
- Add unit tests for new functionality
- Ensure all security features are thoroughly tested
- Update documentation for any user-facing changes

### Security Contributions
For security-related contributions:
- **Responsible Disclosure**: Report vulnerabilities privately first
- **Code Review**: All security-related changes require peer review
- **Testing**: Include security test cases with contributions
- **Documentation**: Update security documentation as needed

### Bug Reports
Please include:
- **Environment details** (OS, Python version)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Log files** (with sensitive data removed)

---

## 📞 Support & Community

### Getting Help
- **Documentation**: Comprehensive guides in this README
- **Issues**: [GitHub Issues](https://github.com/JyotirmaySwarnakar/passguard/issues) for bug reports
- **Discussions**: [GitHub Discussions](https://github.com/JyotirmaySwarnakar/passguard/discussions) for questions

### Project Status
- **Active Development**: Regular updates and security patches
- **Community Driven**: Open to contributions and feedback
- **Security Focused**: Continuous security improvements and audits

---

## ⚠️ Disclaimer

**PassGuard** is designed for personal use and educational purposes. While it implements industry-standard security practices, users should evaluate their own security requirements and consider professional security audits for enterprise use.

- **No Warranty**: This software is provided "as is" without warranty
- **User Responsibility**: Users are responsible for maintaining secure backups
- **Security Updates**: Keep the application and dependencies updated
- **Risk Assessment**: Evaluate security requirements for your specific use case

---

## 📊 Project Metrics

### Security Features
- ✅ **AES-256 Encryption** - Military-grade data protection
- ✅ **bcrypt Password Hashing** - Industry-standard authentication
- ✅ **TOTP 2FA Support** - Multi-factor authentication
- ✅ **Session Management** - Automatic timeout protection
- ✅ **Secure File Permissions** - Unix-level access control
- ✅ **Memory Protection** - Sensitive data clearing
- ✅ **Input Validation** - Comprehensive sanitization
- ✅ **Error Handling** - No information leakage

### Code Quality
- **Python 3.7+ Compatible** - Modern language features
- **Modular Architecture** - Clean separation of concerns  
- **Comprehensive Logging** - Detailed operation tracking
- **Exception Handling** - Graceful error recovery
- **Documentation** - Extensive inline and external docs

---

*Built with ❤️ and 🔒 by Jyotirmay Swarnakar. 