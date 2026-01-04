import json
import os

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
    IMAGE_FOLDER = "images/"
    
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
