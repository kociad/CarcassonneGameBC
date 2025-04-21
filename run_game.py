import os
import subprocess
import sys

def dependencies_met():
    """
    Try importing required packages listed in requirements.txt.
    If all imports succeed, dependencies are considered met.
    """
    try:
        import pygame
        return True
    except ImportError:
        return False

def install_dependencies():
    """
    Run the install_dependencies.py script if dependencies are missing.
    """
    print("🔍 Missing dependencies detected. Installing...")
    subprocess.check_call([sys.executable, "install_dependencies.py"])

def run_game():
    """
    Run the main game script.
    """
    print("🚀 Launching the game...")
    subprocess.run([sys.executable, os.path.join("src", "game.py")])

if __name__ == "__main__":
    if not dependencies_met():
        install_dependencies()

    run_game()
