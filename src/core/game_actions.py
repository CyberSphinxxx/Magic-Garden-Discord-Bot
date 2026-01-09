"""
Game action functions for the Magic Garden Bot.

This module provides high-level game automation functions including:
- Crop harvesting and selling
- Movement
- Auto-buy routines
- Main automation loops
"""

import time
import os

from pynput.keyboard import Key
import pydirectinput
import cv2
import pyautogui
import numpy as np

from . import state
from . import automation
from .config import Config


# =============================================================================
# HOTKEY HELPERS
# =============================================================================

def _press_shift_key(key_char, pre_delay=0.2, post_delay=0.5):
    """
    Press Shift + key combination using pydirectinput.
    
    Args:
        key_char: Character key to press with shift ('1', '2', '3')
        pre_delay: Delay before releasing key
        post_delay: Delay after releasing all keys
    """
    pydirectinput.keyDown('shift')
    time.sleep(pre_delay)
    pydirectinput.keyDown(key_char)
    time.sleep(pre_delay)
    pydirectinput.keyUp(key_char)
    pydirectinput.keyUp('shift')
    time.sleep(post_delay)


def _take_thresholded_screenshot():
    """
    Take a screenshot and apply binary threshold for template matching.
    
    Returns:
        tuple: (screenshot_np, screenshot_gray, screenshot_thresh)
    """
    screenshot = np.array(pyautogui.screenshot())
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    _, screenshot_thresh = cv2.threshold(screenshot_gray, 200, 255, cv2.THRESH_BINARY)
    return screenshot, screenshot_gray, screenshot_thresh


def _match_and_find(screenshot_thresh, template_thresh, threshold=0.8):
    """
    Perform template matching and return location if above threshold.
    
    Args:
        screenshot_thresh: Thresholded screenshot
        template_thresh: Thresholded template
        threshold: Confidence threshold
        
    Returns:
        tuple or None: (max_loc, max_val, match_found)
    """
    result = cv2.matchTemplate(screenshot_thresh, template_thresh, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_loc, max_val, max_val >= threshold


# =============================================================================
# CROP MANAGEMENT
# =============================================================================

def sell_crops(logger=print):
    """Handle selling crops when inventory is full."""
    state.stats['total_sells'] += 1
    state.stats['last_sell_time'] = time.time()
    
    logger(f"📦 Inventory full at ({state.current_position['row']}, {state.current_position['col']}) - Selling...", "warning")
    
    # Save position before leaving to sell
    saved_position = state.current_position.copy()
    
    automation.press_hotkey(Key.shift, '3')  # Open sell menu
    time.sleep(0.3)
    automation.press_key(Key.space)          # Press "Sell All"
    time.sleep(0.5)
 
    go_to_journal_img = os.path.join(Config.IMAGE_FOLDER, "go_to_journal.png")
    journal_btn_loc = automation.locate_image(go_to_journal_img, confidence=Config.CONFIDENCE)
    
    if journal_btn_loc:
        logger("📘 Journal interruption detected! Handling...", "info")
        automation.click_region(journal_btn_loc)
        time.sleep(1.0)  # Wait for journal to open
        
        log_items_img = os.path.join(Config.IMAGE_FOLDER, "log_new_items_in_journal.png")
        if automation.locate_image(log_items_img, confidence=Config.CONFIDENCE):
            logger("📝 Logging new items...", "info")
            automation.press_key(Key.space)
        
        time.sleep(5.0)
        automation.press_key(Key.esc)
        time.sleep(0.5)
        
        logger("🔄 Reselling...", "info")
        
        # Use hotkey instead of clicking image
        automation.press_hotkey(Key.shift, '3')
        time.sleep(0.3)

        automation.press_key(Key.space)
        time.sleep(0.5)

    automation.press_hotkey(Key.shift, '2')
    time.sleep(Config.SELL_RETURN_DELAY)
    
    # Restore position
    state.current_position.update(saved_position)
    
    logger("✓ Crops sold! Resuming harvest...", "success")


# =============================================================================
# MOVEMENT
# =============================================================================

def move(direction, steps=1, logger=print):
    """
    Move in a given direction for a number of steps.
    
    Args:
        direction: 'w', 'a', 's', or 'd'
        steps: Number of steps to move
        logger: Logging function
    """
    # Direction to position delta mapping
    DIRECTION_DELTA = {
        'w': ('row', -1),
        's': ('row', 1),
        'a': ('col', -1),
        'd': ('col', 1),
    }
    
    for _ in range(steps):
        if not state.bot_running:
            return
        
        automation.press_key(direction)
        state.stats['total_moves'] += 1
        
        # Update position
        if direction in DIRECTION_DELTA:
            axis, delta = DIRECTION_DELTA[direction]
            state.current_position[axis] += delta
        
        time.sleep(Config.MOVE_DELAY)
        
        if automation.check_inventory_full():
            sell_crops(logger)


def harvest(logger=print):
    """Harvest the current plot."""
    for _ in range(Config.HARVEST_COUNT):
        if not state.bot_running:
            return
        
        if automation.check_inventory_full():
            sell_crops(logger)
            automation.press_key(Key.space)

        automation.press_key(Key.space)
        time.sleep(Config.HARVEST_DELAY)
    
    state.stats['total_harvests'] += 1


def return_to_start(logger=print):
    """Return to the starting position (0, 0)."""
    # Move up to the first row
    if state.current_position['row'] > 0:
        move('w', state.current_position['row'], logger=logger)
    
    # Move left to the first column
    if state.current_position['col'] > 0:
        move('a', state.current_position['col'], logger=logger)
    
    state.current_position['row'] = 0
    state.current_position['col'] = 0


# =============================================================================
# AUTOBUY HELPERS
# =============================================================================

def _load_autobuy_templates(seeds_to_buy, logger):
    """
    Load all templates needed for autobuy routine.
    
    Args:
        seeds_to_buy: List of seed names
        logger: Logging function
        
    Returns:
        tuple: (seed_templates, buy_thresh, header_thresh) or (None, None, None) on failure
    """
    seed_templates = {}
    for seed_name in seeds_to_buy:
        item_image = f"text_{seed_name.lower().replace(' ', '_')}.png"
        item_template_path = os.path.join(Config.IMAGE_FOLDER, item_image)
        template = cv2.imread(item_template_path, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            _, template_thresh = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
            seed_templates[seed_name] = (template, template_thresh)
        else:
            logger(f"⚠️ Could not load template for {seed_name}", "warning")
    
    # Load buy button template
    buy_button_path = os.path.join(Config.IMAGE_FOLDER, "buy_button_green.png")
    buy_button_template = cv2.imread(buy_button_path, cv2.IMREAD_GRAYSCALE)
    if buy_button_template is None:
        logger("❌ Could not load buy button template", "error")
        return None, None, None
    _, buy_thresh = cv2.threshold(buy_button_template, 200, 255, cv2.THRESH_BINARY)
    
    # Load shop header template
    header_path = os.path.join(Config.IMAGE_FOLDER, "seed_shop_header.png")
    header_template = cv2.imread(header_path, cv2.IMREAD_GRAYSCALE)
    header_thresh = None
    if header_template is not None:
        _, header_thresh = cv2.threshold(header_template, 200, 255, cv2.THRESH_BINARY)
    
    return seed_templates, (buy_button_template, buy_thresh), (header_template, header_thresh)


def _open_shop(logger):
    """
    Open the shop via teleport and interaction.
    
    Returns:
        bool: True if shop opened successfully
    """
    logger("🏪 Teleporting to shop...", "info")
    _press_shift_key('1')
    
    logger("🚪 Opening shop...", "info")
    pydirectinput.keyDown('space')
    time.sleep(0.2)
    pydirectinput.keyUp('space')
    time.sleep(0.5)
    
    # Verify shop is open
    _, screenshot_gray, _ = _take_thresholded_screenshot()
    
    template_path = os.path.join(Config.IMAGE_FOLDER, "seed_shop_header.png")
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    if template is None:
        logger("❌ Could not load shop header template", "error")
        return False
    
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    if max_val < 0.8:
        logger(f"❌ Shop not detected (confidence: {max_val:.2f})", "error")
        return False
    
    logger("✓ Shop opened successfully", "success")
    return True


def _close_shop_and_return(logger):
    """Close shop and return to garden."""
    logger("🚪 Closing shop...", "info")
    pydirectinput.press('esc')
    time.sleep(0.5)
    pydirectinput.press('esc')
    time.sleep(0.5)
    
    logger("🌱 Returning to garden...", "info")
    _press_shift_key('2')


def _buy_seed(seed_name, center_x, center_y, buy_button_data, seeds_per_trip, logger):
    """
    Attempt to buy a seed at the given location.
    
    Args:
        seed_name: Name of the seed
        center_x, center_y: Click location
        buy_button_data: (template, thresh) tuple for buy button
        seeds_per_trip: Number to purchase
        logger: Logging function
        
    Returns:
        bool: True if purchase successful
    """
    buy_button_template, buy_thresh = buy_button_data
    
    logger(f"🖱️ Clicking on {seed_name}...", "info")
    pyautogui.click(center_x, center_y)
    time.sleep(1.0)  # Wait for dropdown
    
    # Take new screenshot to find buy button
    _, _, screenshot_thresh = _take_thresholded_screenshot()
    
    max_loc, max_val, found = _match_and_find(screenshot_thresh, buy_thresh)
    
    if found:
        btn_height, btn_width = buy_button_template.shape
        btn_center_x = max_loc[0] + btn_width // 2
        btn_center_y = max_loc[1] + btn_height // 2
        
        logger(f"💰 Purchasing {seeds_per_trip}x {seed_name}...", "info")
        for _ in range(seeds_per_trip):
            pyautogui.click(btn_center_x, btn_center_y)
            time.sleep(0.3)
        
        logger(f"✓ Purchased {seeds_per_trip}x {seed_name}!", "success")
        return True
    else:
        logger(f"⚠️ Could not find buy button for {seed_name} (out of stock?)", "warning")
        return False


# =============================================================================
# AUTOBUY ROUTINE
# =============================================================================

def run_autobuy_routine(logger=print):
    """Execute auto-buy routine to purchase all selected seeds from the shop."""
    try:
        # Get list of seeds to buy
        seeds_to_buy = getattr(Config, 'SELECTED_SEEDS', None)
        if not seeds_to_buy:
            seeds_to_buy = [Config.SELECTED_SEED] if Config.SELECTED_SEED else []
        
        if not seeds_to_buy:
            logger("⚠️ No seeds selected for auto-buy!", "warning")
            return False
        
        logger(f"🛒 Starting auto-buy routine for {len(seeds_to_buy)} seed(s)...", "info")
        
        # Open shop
        if not _open_shop(logger):
            return False
        
        # Check if stopped
        if not state.bot_running:
            logger("⏹️ Autobuy stopped by user", "warning")
            pydirectinput.press('escape')
            return False
        
        # Load templates
        templates = _load_autobuy_templates(seeds_to_buy, logger)
        seed_templates, buy_button_data, header_data = templates
        
        if buy_button_data is None:
            pydirectinput.press('escape')
            return False
        
        buy_button_template, buy_thresh = buy_button_data
        header_template, header_thresh = header_data
        
        # Single-pass approach
        remaining_seeds = list(seeds_to_buy)
        seeds_bought = 0
        max_scrolls = getattr(Config, 'SHOP_SEARCH_ATTEMPTS', 7)
        seeds_per_trip = getattr(Config, 'SEEDS_PER_TRIP', 1)
        
        logger(f"🔍 Searching for {len(remaining_seeds)} seed(s) in single pass...", "info")
        
        for scroll_idx in range(max_scrolls):
            if not state.bot_running:
                logger("⏹️ Autobuy stopped by user", "warning")
                pydirectinput.press('escape')
                return False
            
            if not remaining_seeds:
                logger("✓ All seeds found and purchased!", "success")
                break
            
            # Take screenshot
            _, _, screenshot_thresh = _take_thresholded_screenshot()
            
            # Check for each remaining seed
            seeds_found_this_view = []
            for seed_name in remaining_seeds[:]:
                if seed_name not in seed_templates:
                    remaining_seeds.remove(seed_name)
                    continue
                
                template, template_thresh = seed_templates[seed_name]
                max_loc, max_val, found = _match_and_find(screenshot_thresh, template_thresh)
                
                if found:
                    template_height, template_width = template.shape
                    center_x = max_loc[0] + template_width // 2
                    center_y = max_loc[1] + template_height // 2
                    seeds_found_this_view.append((seed_name, center_x, center_y, max_val))
            
            # Buy seeds found (sorted by Y position)
            seeds_found_this_view.sort(key=lambda x: x[2])
            
            for seed_name, center_x, center_y, confidence in seeds_found_this_view:
                if not state.bot_running:
                    pydirectinput.press('escape')
                    return False
                
                logger(f"✓ Found {seed_name} at ({center_x}, {center_y})", "success")
                
                if _buy_seed(seed_name, center_x, center_y, buy_button_data, seeds_per_trip, logger):
                    seeds_bought += seeds_per_trip
                
                remaining_seeds.remove(seed_name)
                time.sleep(0.3)
            
            if not remaining_seeds:
                break
            
            # Scroll down
            if scroll_idx < max_scrolls - 1:
                _scroll_shop(screenshot_thresh, header_template, header_thresh, scroll_idx, max_scrolls, logger)
        
        # Report any seeds not found
        if remaining_seeds:
            logger(f"⚠️ Could not find: {', '.join(remaining_seeds)}", "warning")
        
        _close_shop_and_return(logger)
        
        logger(f"✓ Auto-buy completed! Bought {seeds_bought} from {len(seeds_to_buy)} seed type(s).", "success")
        return seeds_bought > 0
        
    except Exception as e:
        logger(f"❌ Auto-buy error: {e}", "error")
        return False


def _scroll_shop(screenshot_thresh, header_template, header_thresh, scroll_idx, max_scrolls, logger):
    """Scroll shop to find more seeds."""
    if header_thresh is None:
        return
    
    max_loc, max_val, found = _match_and_find(screenshot_thresh, header_thresh, threshold=0.7)
    
    if found:
        header_h, header_w = header_template.shape
        header_center_x = max_loc[0] + header_w // 2
        scroll_y = max_loc[1] + header_h // 2 + 200
        
        pyautogui.moveTo(header_center_x, scroll_y)
        time.sleep(0.3)
        pyautogui.scroll(-600)
        time.sleep(1.0)
        logger(f"📜 Scrolling... ({scroll_idx + 1}/{max_scrolls})", "info")
    else:
        # Try to recover shop view
        logger("⚠️ Shop header lost, attempting recovery...", "warning")
        pydirectinput.press('escape')
        time.sleep(0.3)
        _press_shift_key('1')
        pydirectinput.press('space')
        time.sleep(1.0)


# =============================================================================
# AUTOBUY TIMER HELPER
# =============================================================================

def _check_autobuy_timer(logger):
    """
    Check if autobuy timer has triggered and run autobuy if needed.
    
    Returns:
        bool: True if autobuy was triggered
    """
    if not Config.AUTOBUY_ENABLED or 'last_buy_time' not in state.stats:
        return False
    
    time_remaining = Config.AUTOBUY_INTERVAL - (time.time() - state.stats['last_buy_time'])
    state.stats['next_buy_time'] = max(0, time_remaining)
    
    if time_remaining <= 0:
        logger(f"⏰ Auto-buy timer reached - pausing harvest...", "warning")
        if run_autobuy_routine(logger):
            state.stats['last_buy_time'] = time.time()
            state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
            logger("✓ Auto-buy complete. Resuming harvest...", "success")
        else:
            logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
            state.stats['last_buy_time'] = time.time()
        return True
    
    return False


# =============================================================================
# MAIN AUTOMATION LOOPS
# =============================================================================

def harvest_loop(logger=print):
    """
    Main automation loop that handles harvesting and/or auto-buy based on configuration.
    
    Supports three modes:
    1. Harvesting + Auto-Buy
    2. Harvesting only
    3. Auto-Buy only
    """
    # Validate configuration
    if not Config.HARVESTING_ENABLED and not Config.AUTOBUY_ENABLED:
        logger("⚠️ ERROR: Both Harvesting and Auto-Buy are disabled!", "error")
        logger("⚠️ Please enable at least one mode in configuration.", "error")
        state.bot_running = False
        return
    
    # Initialize auto-buy timer
    if Config.AUTOBUY_ENABLED and 'last_buy_time' not in state.stats:
        state.stats['last_buy_time'] = time.time()
    
    # Log active modes
    modes = []
    if Config.HARVESTING_ENABLED:
        modes.append("Harvesting")
    if Config.AUTOBUY_ENABLED:
        modes.append("Auto-Buy")
    logger(f"🤖 Bot running in mode: {' + '.join(modes)}", "info")
    
    if Config.HARVESTING_ENABLED:
        _run_harvesting_mode(logger)
    else:
        _run_autobuy_only_mode(logger)


def _run_harvesting_mode(logger):
    """Execute harvesting mode with optional auto-buy."""
    state.current_position['row'] = 0
    state.current_position['col'] = 0
    
    # Update autobuy timer display
    if Config.AUTOBUY_ENABLED and 'last_buy_time' in state.stats:
        state.stats['next_buy_time'] = max(0, Config.AUTOBUY_INTERVAL - (time.time() - state.stats['last_buy_time']))
    
    # Harvest in snake pattern
    for row in range(Config.ROWS):
        if not state.bot_running:
            return
        
        state.current_position['row'] = row
        
        if row % 2 == 0:
            # Move right on even rows
            for col in range(Config.COLUMNS):
                if not state.bot_running:
                    return
                state.current_position['col'] = col
                _check_autobuy_timer(logger)
                harvest(logger)
                if col < Config.COLUMNS - 1:
                    move('d', logger=logger)
        else:
            # Move left on odd rows
            for col in range(Config.COLUMNS - 1, -1, -1):
                if not state.bot_running:
                    return
                state.current_position['col'] = col
                _check_autobuy_timer(logger)
                harvest(logger)
                if col > 0:
                    move('a', logger=logger)
        
        # Move down to next row
        if row < Config.ROWS - 1:
            move('s', logger=logger)
    
    # Return to start
    if state.bot_running:
        logger("✓ Grid finished. Returning to start...", "info")
        return_to_start(logger)


def _run_autobuy_only_mode(logger):
    """Execute auto-buy only mode (no harvesting)."""
    logger("🛒 Auto-buy only mode - waiting for next purchase cycle...", "info")
    
    while state.bot_running:
        current_time = time.time()
        time_remaining = Config.AUTOBUY_INTERVAL - (current_time - state.stats['last_buy_time'])
        
        state.stats['next_buy_time'] = max(0, time_remaining)
        
        if time_remaining <= 0:
            logger(f"⏰ Auto-buy timer reached ({Config.AUTOBUY_INTERVAL}s)", "warning")
            if run_autobuy_routine(logger):
                state.stats['last_buy_time'] = current_time
                state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                logger("✓ Auto-buy complete. Waiting for next cycle...", "success")
            else:
                logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                state.stats['last_buy_time'] = current_time
        else:
            if time_remaining > 10:
                logger(f"⏳ Next auto-buy in {int(time_remaining)}s...", "info")
            time.sleep(1)


def run_shop_only_loop(logger=print):
    """
    Dedicated shop-only automation loop.
    
    Loops indefinitely while state.bot_running is True.
    Checks the auto-buy interval timer and triggers purchases.
    Does NOT move the character - just idles and shops.
    """
    logger("🛒 Starting dedicated Shop Mode...", "info")
    
    # Initialize last_buy_time to start in 5 seconds
    if 'last_buy_time' not in state.stats:
        state.stats['last_buy_time'] = time.time() - (Config.AUTOBUY_INTERVAL - 5)
    
    while state.bot_running:
        current_time = time.time()
        elapsed = current_time - state.stats.get('last_buy_time', current_time)
        time_remaining = Config.AUTOBUY_INTERVAL - elapsed
        
        state.stats['next_buy_time'] = max(0, time_remaining)
        
        if time_remaining <= 0:
            logger(f"⏰ Auto-buy timer reached ({Config.AUTOBUY_INTERVAL}s)", "warning")
            if run_autobuy_routine(logger):
                state.stats['last_buy_time'] = time.time()
                state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                logger("✓ Auto-buy complete. Waiting for next cycle...", "success")
            else:
                logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                state.stats['last_buy_time'] = time.time()
        else:
            time.sleep(1)
    
    logger("🛒 Shop Mode stopped.", "info")
