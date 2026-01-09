"""
Constants and data definitions for the Magic Garden Bot GUI.

This module centralizes all hardcoded data, color palettes, and configuration
defaults to improve maintainability and reduce duplication.
"""

# =============================================================================
# COLOR PALETTES
# =============================================================================

# Discord-inspired color palette for the UI
UI_COLORS = {
    'window_bg': "#2b2d31",
    'sidebar_bg': "#313338",
    'card_bg': "#2f3136",
    'blurple': "#5865F2",
    'green': "#2EA043",
    'red': "#ED4245",
    'text_primary': "#FFFFFF",
    'text_secondary': "#B5BAC1",
    'text_muted': "#949BA4",
}

# Rarity tier colors for seeds
RARITY_COLORS = {
    'COMMON': '#FFFFFF',      # Common (White)
    'UNCOMMON': '#2EA043',    # Uncommon (Green)
    'RARE': '#3B8ED0',        # Rare (Blue)
    'LEGENDARY': '#FFD700',   # Legendary (Gold/Yellow)
    'MYTHICAL': '#A855F7',    # Mythical (Purple)
    'DIVINE': '#FF7530',      # Divine (Darker/Vivid Orange)
    'CELESTIAL': '#FF69B4',   # Celestial (Pink)
}


# =============================================================================
# SEED DATA
# =============================================================================

# Seeds organized by tier: (tier_name, color, [seeds])
SEED_TIERS = [
    ("COMMON", RARITY_COLORS['COMMON'], ['Carrot', 'Strawberry', 'Aloe']),
    ("UNCOMMON", RARITY_COLORS['UNCOMMON'], ['Fava Bean', 'Blueberry', 'Apple', 'Tulip', 'Tomato']),
    ("RARE", RARITY_COLORS['RARE'], ['Daffodil', 'Corn', 'Watermelon', 'Pumpkin', 'Echeveria']),
    ("LEGENDARY", RARITY_COLORS['LEGENDARY'], ['Coconut', 'Banana', 'Lily', 'Camellia', "Burro's Tail"]),
    ("MYTHICAL", RARITY_COLORS['MYTHICAL'], ['Mushroom', 'Cactus', 'Bamboo', 'Chrysanthemum', 'Grape']),
    ("DIVINE", RARITY_COLORS['DIVINE'], ['Pepper', 'Lemon', 'Passion Fruit', 'Dragon Fruit', 'Cacao', 'Lychee', 'Sunflower']),
    ("CELESTIAL", RARITY_COLORS['CELESTIAL'], ['Starweaver', 'Dawnbinder', 'Moonbinder']),
]

# Flat list of all seeds (derived from SEED_TIERS)
ALL_SEEDS = [
    'Carrot', 'Strawberry', 'Aloe', 'Fava Bean', 'Blueberry', 'Apple',
    'Tulip', 'Tomato', 'Daffodil', 'Corn', 'Watermelon', 'Pumpkin',
    'Echeveria', 'Coconut', 'Banana', 'Lily', 'Camellia', "Burro's Tail",
    'Mushroom', 'Cactus', 'Bamboo', 'Chrysanthemum', 'Grape', 'Pepper',
    'Lemon', 'Passion Fruit', 'Dragon Fruit', 'Cacao', 'Lychee', 'Sunflower',
    'Starweaver', 'Dawnbinder', 'Moonbinder'
]


def get_seed_color_map():
    """
    Build a dictionary mapping seed names to their rarity colors.
    
    Returns:
        dict: {seed_name: hex_color}
    """
    seed_colors = {}
    for _, color, seeds in SEED_TIERS:
        for seed in seeds:
            seed_colors[seed] = color
    return seed_colors


# =============================================================================
# CONFIGURATION DEFAULTS
# =============================================================================

# Default configuration values for reset
DEFAULT_CONFIGS = {
    'COLUMNS': '10',
    'HARVEST_COUNT': '5',
    'MOVE_DELAY': '0.12',
    'HARVEST_DELAY': '0.1',
    'LOOP_COOLDOWN': '2',
}

# Configuration field definitions: (label, config_key, min_val, max_val, tooltip)
CONFIG_DEFINITIONS = [
    ("Columns", "COLUMNS", 1, 20, "Number of columns in the garden grid."),
    ("Harvest Count", "HARVEST_COUNT", 1, 10, "How many times to click each crop tile."),
    ("Move Delay (s)", "MOVE_DELAY", 0.05, 1.0, "Time in seconds between grid movements (Recommended: 0.12s)."),
    ("Harvest Delay (s)", "HARVEST_DELAY", 0.05, 1.0, "Time to wait after clicking a crop."),
    ("Loop Cooldown (s)", "LOOP_COOLDOWN", 0, 10, "Pause time between full garden cycles."),
]


# =============================================================================
# UI CONSTANTS
# =============================================================================

# Inventory grid columns
INVENTORY_COLUMNS = 4

# View modes for inventory display
VIEW_MODES = ["Grid", "Tier", "A-Z"]

# Button dimensions
BUTTON_HEIGHT = 40
BUTTON_WIDTH_SMALL = 60
BUTTON_WIDTH_MEDIUM = 100

# Font configurations
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"
