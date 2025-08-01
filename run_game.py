import os
import subprocess
import sys

def dependenciesMet():
    """
    Try importing required packages listed in requirements.txt.
    If all imports succeed, dependencies are considered met.
    """
    try:
        import pygame
        return True
    except ImportError:
        return False

def installDependencies():
    """
    Run the install_dependencies.py script if dependencies are missing.
    """
    print("🔍 Missing dependencies detected. Installing...")
    subprocess.check_call([sys.executable, "install_dependencies.py"])

def runGame():
    """
    Run the main game script.
    """
    print("🚀 Launching the game...")
    subprocess.run([sys.executable, os.path.join("src", "game.py")])

if __name__ == "__main__":
    if not dependenciesMet():
        installDependencies()

    runGame()
