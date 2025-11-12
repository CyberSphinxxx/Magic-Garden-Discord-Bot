import sys
import os
import tkinter as tk

# Add the project root to the Python path to allow direct execution of this script
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.config import Config
from src.gui.main_window import HarvestBotGUI

def main():
    """
    Initializes and runs the Magic Garden Bot application.
    """
    # Load the configuration at the very start
    Config.load()

    # Set up the main GUI window
    root = tk.Tk()
    
    # The HarvestBotGUI class now handles all application logic.
    # We just need to create an instance of it.
    app = HarvestBotGUI(root)

    # Start the application's main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
