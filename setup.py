#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
from pathlib import Path

class PassGuardSetup:
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = platform.system()
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"

    def check_python_version(self):
        print("🐍 Checking Python version...")
        if self.python_version < (3, 7):
            print(f"❌ Python 3.7+ required. Current version: {sys.version}")
            return False
        print(f"✅ Python {sys.version.split()[0]} - Compatible!")
        return True

    def check_platform(self):
        print(f"💻 Detected platform: {self.platform}")
        if self.platform not in ["Linux", "Darwin"]:
            print("⚠️  This app is designed for Linux/macOS.")
            if input("Continue anyway? (y/N): ").lower() != 'y':
                return False
        print("✅ Platform supported!")
        return True

    def install_dependencies(self):
        print("📦 Installing dependencies...")
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Dependencies installed successfully!")
                return True
            print(f"❌ Failed to install dependencies:\n{result.stderr}")
            return False
        except subprocess.CalledProcessError:
            print("❌ pip not found! Please install pip and try again.")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False

    def create_desktop_entry(self):
        if self.platform != "Linux":
            return True
        try:
            desktop_dir = Path.home() / ".local/share/applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            desktop_file = desktop_dir / "passguard.desktop"
            script_path = self.project_root / "main.py"
            desktop_content = f"""[Desktop Entry]
Name=PassGuard
Comment=Secure local password manager
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
            return True

    def create_shell_alias(self):
        script_path = self.project_root / "main.py"
        alias_cmd = f"alias passguard='python3 {script_path}'"
        print("\n💡 Tip: Add this alias to your shell profile:")
        print(f"   {alias_cmd}")
        shell_profiles = [Path.home() / ".bashrc", Path.home() / ".zshrc", Path.home() / ".profile"]
        existing_profiles = [p for p in shell_profiles if p.exists()]
        if existing_profiles:
            print(f"\n🔧 Found profiles: {', '.join(p.name for p in existing_profiles)}")
            if input("Add alias automatically? (y/N): ").lower() == 'y':
                try:
                    for profile in existing_profiles:
                        with open(profile, 'a') as f:
                            f.write(f"\n# PassGuard alias\n{alias_cmd}\n")
                    print("✅ Alias added! Run 'source ~/.bashrc' to apply.")
                except Exception as e:
                    print(f"⚠️  Could not add alias: {e}")

    def run_setup(self):
        print("=" * 50)
        print("🔐 PASSGUARD SETUP")
        print("=" * 50)
        if not self.check_python_version():
            return False
        if not self.check_platform():
            return False
        if not self.install_dependencies():
            print("\n❌ Setup failed due to dependency issues.")
            return False
        self.create_desktop_entry()
        self.create_shell_alias()
        print("\n" + "=" * 50)
        print("🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("🚀 Launch with:")
        print(f"   python3 {self.project_root / 'main.py'}")
        print("🔒 Passwords will be stored in: ~/.PassGuard/")
        print("📖 See README.md for usage.")
        print("=" * 50)
        return True

def main():
    setup = PassGuardSetup()
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
