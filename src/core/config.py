import json
import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource (works for dev and PyInstaller .exe).
    
    When running as a PyInstaller bundle, files are extracted to a temp
    directory stored in sys._MEIPASS. When running as a script, we use
    the current working directory.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running as script - use current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Config:
    """
    Handles loading and saving of the bot's configuration.
    """
    ROWS = 10
    COLUMNS = 10
    HARVEST_COUNT = 5
    CONFIDENCE = 0.8
    INVENTORY_CONFIDENCE = 0.6  # Lower threshold for inventory detection to handle GPU color variations (AMD vs NVIDIA)
    MOVE_DELAY = 0.15
    HARVEST_DELAY = 0.1
    LOOP_COOLDOWN = 2
    SELL_RETURN_DELAY = 1.0
    POST_PURCHASE_CLICK_DELAY = 0.3  # Delay before clicking seed to close menu after purchase
    POST_PURCHASE_MENU_CLOSE_WAIT = 0.5  # Wait time after clicking seed to ensure menu closes
    # Use resource_path for PyInstaller compatibility
    # Note: .spec file bundles 'src/images' as 'images', so we check both paths
    IMAGE_FOLDER = resource_path("images") if hasattr(sys, '_MEIPASS') else "src/images/"
    AUTOBUY_ENABLED = False
    SELECTED_SEED = 'Carrot'
    SELECTED_SEEDS = ['Carrot']  # List of seeds to buy in order
    HARVESTING_ENABLED = True
    AUTOBUY_INTERVAL = 180  # Default 3 minutes in seconds
    SEEDS_PER_TRIP = 1  # Number of each seed to buy per shop visit
    SHOP_SEARCH_ATTEMPTS = 7  # Number of scroll attempts to find a seed
    
    # Auto-Update Settings
    AUTO_UPDATE_CHECK = True  # Check for updates on startup
    UPDATE_SKIPPED_VERSION = None  # Version user chose to skip
    
    @classmethod
    def save(cls):
        """Save config to a JSON file in the user's home directory."""
        config_dict = {
            'ROWS': cls.ROWS,
            'COLUMNS': cls.COLUMNS,
            'HARVEST_COUNT': cls.HARVEST_COUNT,
            'MOVE_DELAY': cls.MOVE_DELAY,
            'HARVEST_DELAY': cls.HARVEST_DELAY,
            'LOOP_COOLDOWN': cls.LOOP_COOLDOWN,
            'SELL_RETURN_DELAY': cls.SELL_RETURN_DELAY,
            'POST_PURCHASE_CLICK_DELAY': cls.POST_PURCHASE_CLICK_DELAY,
            'POST_PURCHASE_MENU_CLOSE_WAIT': cls.POST_PURCHASE_MENU_CLOSE_WAIT,
            'AUTOBUY_ENABLED': cls.AUTOBUY_ENABLED,
            'SELECTED_SEED': cls.SELECTED_SEED,
            'SELECTED_SEEDS': cls.SELECTED_SEEDS,
            'HARVESTING_ENABLED': cls.HARVESTING_ENABLED,
            'AUTOBUY_INTERVAL': cls.AUTOBUY_INTERVAL,
            'SEEDS_PER_TRIP': cls.SEEDS_PER_TRIP,
            'SHOP_SEARCH_ATTEMPTS': cls.SHOP_SEARCH_ATTEMPTS,
            'AUTO_UPDATE_CHECK': cls.AUTO_UPDATE_CHECK,
            'UPDATE_SKIPPED_VERSION': cls.UPDATE_SKIPPED_VERSION,
        }
        try:
            # Save config in a user-specific, persistent location
            config_path = os.path.join(os.path.expanduser('~'), 'magic_garden_bot_config.json')
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=4)
        except Exception as e:
            print(f"Could not save config: {e}")
    
    @classmethod
    def load(cls):
        """Load config from a JSON file in the user's home directory."""
        try:
            config_path = os.path.join(os.path.expanduser('~'), 'magic_garden_bot_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
                    for key, value in config_dict.items():
                        if key == 'IMAGE_FOLDER':
                            continue
                        setattr(cls, key, value)
        except Exception as e:
            print(f"Could not load config: {e}")
