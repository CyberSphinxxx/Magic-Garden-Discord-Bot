import sys
import os
import customtkinter as ctk



from src.core.config import Config
from src.gui.main_window import HarvestBotGUI

def main():
    """
    Initializes and runs the Magic Garden Bot application.
    """
    # Load the configuration at the very start
    Config.load()

    # Set up customtkinter appearance
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Set up the main GUI window
    root = ctk.CTk()
    
    # The HarvestBotGUI class now handles all application logic.
    # We just need to create an instance of it.
    app = HarvestBotGUI(root)
    
    # Check for updates on startup (runs silently in background)
    app.check_for_updates_on_startup()

    # Start the application's main event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed.")
        root.destroy()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass  # Silent exit on Ctrl+C

