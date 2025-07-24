#!/usr/bin/env python3
"""
Password Manager Setup Script
Handles installation, dependency checking, and initial setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class PasswordManagerSetup:
    """Setup manager for the Password Manager application."""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = platform.system()
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("🐍 Checking Python version...")
        
        if self.python_version < (3, 7):
            print(f"❌ Python 3.7+ required. Current version: {sys.version}")
            print("Please upgrade Python and try again.")
            return False
        
        print(f"✅ Python {sys.version.split()[0]} - Compatible!")
        return True
    
    def check_platform(self):
        """Check if platform is supported."""
        print(f"💻 Detected platform: {self.platform}")
        
        if self.platform not in ["Linux", "Darwin"]:  # Linux and macOS
            print("⚠️  Warning: This application is designed for Unix-like systems.")
            print("Some security features may not work properly on Windows.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        print("✅ Platform supported!")
        return True
    
    def install_dependencies(self):
        """Install required Python packages."""
        print("📦 Installing dependencies...")
        
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False
        
        try:
            # Check if pip is available
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            
            # Install requirements
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully!")
                return True
            else:
                print(f"❌ Failed to install dependencies:")
                print(result.stderr)
                return False
                
        except subprocess.CalledProcessError:
            print("❌ pip not found! Please install pip and try again.")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def create_desktop_entry(self):
        """Create desktop entry for Linux systems."""
        if self.platform != "Linux":
            return True
        
        try:
            desktop_dir = Path.home() / ".local/share/applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = desktop_dir / "password-manager.desktop"
            script_path = self.project_root / "main.py"
            
            desktop_content = f"""[Desktop Entry]
Name=Password Manager
Comment=Secure local password storage
Exec={sys.executable} {script_path}
Icon=dialog-password
Terminal=true
Type=Application
Categories=Utility;Security;
StartupNotify=false
"""
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            desktop_file.chmod(0o755)
            print("✅ Desktop entry created!")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not create desktop entry: {e}")
            return True  # Not critical
    
    def create_shell_alias(self):
        """Suggest shell alias creation."""
        script_path = self.project_root / "main.py"
        alias_cmd = f"alias passman='python3 {script_path}'"
        
        print("\n💡 Tip: Add this alias to your shell profile for easy access:")
        print(f"   {alias_cmd}")
        
        shell_profiles = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile"
        ]
        
        existing_profiles = [p for p in shell_profiles if p.exists()]
        
        if existing_profiles:
            print(f"\n🔧 Found shell profiles: {', '.join(p.name for p in existing_profiles)}")
            response = input("Add alias automatically? (y/N): ")
            
            if response.lower() == 'y':
                try:
                    for profile in existing_profiles:
                        with open(profile, 'a') as f:
                            f.write(f"\n# Password Manager alias\n{alias_cmd}\n")
                    print("✅ Alias added! Restart your terminal or run 'source ~/.bashrc'")
                except Exception as e:
                    print(f"⚠️  Could not add alias: {e}")
    
    def run_setup(self):
        """Run the complete setup process."""
        print("=" * 50)
        print("🔐 PASSWORD MANAGER SETUP")
        print("=" * 50)
        
        # Check system requirements
        if not self.check_python_version():
            return False
        
        if not self.check_platform():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            print("\n❌ Setup failed! Please resolve dependency issues.")
            return False
        
        # Optional enhancements
        self.create_desktop_entry()
        self.create_shell_alias()
        
        # Success message
        print("\n" + "=" * 50)
        print("🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("🚀 Run the password manager with:")
        print(f"   python3 {self.project_root / 'main.py'}")
        print("\n🔒 Your passwords will be stored securely in:")
        print("   ~/.local_passman/")
        print("\n📖 Read README.md for detailed usage instructions.")
        print("=" * 50)
        
        return True

def main():
    """Main setup function."""
    setup = PasswordManagerSetup()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()