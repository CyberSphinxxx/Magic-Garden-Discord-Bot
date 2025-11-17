import sys
import os
import tkinter as tk



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
