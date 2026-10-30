import sys
import os

# Ensure project root and gui are on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

GUI_DIR = os.path.join(BASE_DIR, "gui")
if GUI_DIR not in sys.path:
    sys.path.insert(0, GUI_DIR)

from gui.app import main

if __name__ == "__main__":
    main()
