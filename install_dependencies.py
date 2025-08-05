import subprocess
import sys


def install_requirements():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies.")
        print(e)


if __name__ == "__main__":
    install_requirements()
