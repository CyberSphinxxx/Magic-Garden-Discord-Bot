import time
from pynput.keyboard import Key
import pydirectinput
import cv2
import pyautogui
import numpy as np

from . import state
from . import automation
from .config import Config
import os

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
        time.sleep(1.0) # Wait for journal to open
        
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

def move(direction, steps=1, logger=print):
    """Move in a given direction for a number of steps."""
    for _ in range(steps):
        if not state.bot_running:
            return
        
        automation.press_key(direction)
        state.stats['total_moves'] += 1
        
        # Update position in state
        if direction == 'w':
            state.current_position['row'] -= 1
        elif direction == 's':
            state.current_position['row'] += 1
        elif direction == 'a':
            state.current_position['col'] -= 1
        elif direction == 'd':
            state.current_position['col'] += 1
        
        time.sleep(Config.MOVE_DELAY)
        
        if automation.check_inventory_full():
            sell_crops(logger)

def harvest(logger=print):
    """Harvest the current plot."""
    for _ in range(Config.HARVEST_COUNT):
        if not state.bot_running:
            return
        # Simplified harvesting by removing the image check, as requested.
        # The bot will now always press spacebar to harvest.
        # if not automation.check_harvest_button():
        #     return
        if automation.check_inventory_full():
            sell_crops(logger)
            automation.press_key(Key.space)

        automation.press_key(Key.space)
        time.sleep(Config.HARVEST_DELAY)
    state.stats['total_harvests'] += 1

def return_to_start(logger=print):
    """Return to the starting position (0, 0)."""
    last_row_index = Config.ROWS - 1
    
    # Move up to the first row
    if state.current_position['row'] > 0:
        move('w', state.current_position['row'], logger=logger)
    
    # Move left to the first column
    if state.current_position['col'] > 0:
        move('a', state.current_position['col'], logger=logger)
    
    state.current_position['row'] = 0
    state.current_position['col'] = 0

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
        
        # Open shop: Shift+1 then Space
        logger("🏪 Teleporting to shop...", "info")
        pydirectinput.keyDown('shift')
        time.sleep(0.2)
        pydirectinput.keyDown('1')
        time.sleep(0.2)
        pydirectinput.keyUp('1')
        pydirectinput.keyUp('shift')
        time.sleep(0.5)
        
        logger("🚪 Opening shop...", "info")
        pydirectinput.keyDown('space')
        time.sleep(0.2)
        pydirectinput.keyUp('space')
        time.sleep(0.5)
        
        # Verify shop is open
        screenshot = np.array(pyautogui.screenshot())
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        template_path = os.path.join(Config.IMAGE_FOLDER, "seed_shop_header.png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if template is None:
            logger(f"❌ Could not load shop header template", "error")
            return False
        
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        if max_val < 0.8:
            logger(f"❌ Shop not detected (confidence: {max_val:.2f})", "error")
            return False
        
        logger("✓ Shop opened successfully", "success")
        
        # Check if stopped
        if not state.bot_running:
            logger("⏹️ Autobuy stopped by user", "warning")
            pydirectinput.press('escape')
            return False
        
        # === SINGLE-PASS APPROACH ===
        # Scroll through shop once, checking for ALL remaining seeds at each position
        
        remaining_seeds = list(seeds_to_buy)  # Copy of seeds still to buy
        seeds_bought = 0
        max_scrolls = getattr(Config, 'SHOP_SEARCH_ATTEMPTS', 7)
        seeds_per_trip = getattr(Config, 'SEEDS_PER_TRIP', 1)
        
        # Load all seed templates upfront
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
        if buy_button_template is not None:
            _, buy_thresh = cv2.threshold(buy_button_template, 200, 255, cv2.THRESH_BINARY)
        else:
            logger("❌ Could not load buy button template", "error")
            pydirectinput.press('escape')
            return False
        
        # Load shop header template
        header_path = os.path.join(Config.IMAGE_FOLDER, "seed_shop_header.png")
        header_template = cv2.imread(header_path, cv2.IMREAD_GRAYSCALE)
        header_thresh = None
        if header_template is not None:
            _, header_thresh = cv2.threshold(header_template, 200, 255, cv2.THRESH_BINARY)
        
        logger(f"🔍 Searching for {len(remaining_seeds)} seed(s) in single pass...", "info")
        
        for scroll_idx in range(max_scrolls):
            # Check if stopped
            if not state.bot_running:
                logger("⏹️ Autobuy stopped by user", "warning")
                pydirectinput.press('escape')
                return False
            
            # Check if all seeds bought
            if not remaining_seeds:
                logger("✓ All seeds found and purchased!", "success")
                break
            
            # Take screenshot
            screenshot = np.array(pyautogui.screenshot())
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            _, screenshot_thresh = cv2.threshold(screenshot_gray, 200, 255, cv2.THRESH_BINARY)
            
            # Check for each remaining seed in current view
            seeds_found_this_view = []
            for seed_name in remaining_seeds[:]:  # Iterate over a copy
                if seed_name not in seed_templates:
                    remaining_seeds.remove(seed_name)
                    continue
                
                template, template_thresh = seed_templates[seed_name]
                result = cv2.matchTemplate(screenshot_thresh, template_thresh, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= 0.8:
                    template_height, template_width = template.shape
                    center_x = max_loc[0] + template_width // 2
                    center_y = max_loc[1] + template_height // 2
                    seeds_found_this_view.append((seed_name, center_x, center_y, max_val))
            
            # Buy all seeds found in this view (sorted by Y position - top to bottom)
            seeds_found_this_view.sort(key=lambda x: x[2])  # Sort by Y coordinate
            
            for seed_name, center_x, center_y, confidence in seeds_found_this_view:
                if not state.bot_running:
                    pydirectinput.press('escape')
                    return False
                
                logger(f"✓ Found {seed_name} at ({center_x}, {center_y})", "success")
                
                # Click on the seed
                logger(f"🖱️ Clicking on {seed_name}...", "info")
                pyautogui.click(center_x, center_y)
                time.sleep(1.0)  # Wait for dropdown
                
                # Take new screenshot to find buy button
                screenshot = np.array(pyautogui.screenshot())
                screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
                _, screenshot_thresh = cv2.threshold(screenshot_gray, 200, 255, cv2.THRESH_BINARY)
                
                result = cv2.matchTemplate(screenshot_thresh, buy_thresh, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= 0.8:
                    btn_height, btn_width = buy_button_template.shape
                    btn_center_x = max_loc[0] + btn_width // 2
                    btn_center_y = max_loc[1] + btn_height // 2
                    
                    logger(f"💰 Purchasing {seeds_per_trip}x {seed_name}...", "info")
                    for _ in range(seeds_per_trip):
                        pyautogui.click(btn_center_x, btn_center_y)
                        time.sleep(0.3)
                    
                    logger(f"✓ Purchased {seeds_per_trip}x {seed_name}!", "success")
                    seeds_bought += seeds_per_trip
                    remaining_seeds.remove(seed_name)
                else:
                    logger(f"⚠️ Could not find buy button for {seed_name} (out of stock?)", "warning")
                    remaining_seeds.remove(seed_name)  # Remove anyway to prevent infinite loop
                
                time.sleep(0.3)
            
            # If all seeds bought, stop scrolling
            if not remaining_seeds:
                break
            
            # Scroll down to find more seeds
            if scroll_idx < max_scrolls - 1:
                # Find header to position scroll
                if header_thresh is not None:
                    header_result = cv2.matchTemplate(screenshot_thresh, header_thresh, cv2.TM_CCOEFF_NORMED)
                    _, header_max_val, _, header_max_loc = cv2.minMaxLoc(header_result)
                    
                    if header_max_val >= 0.7:
                        header_h, header_w = header_template.shape
                        header_center_x = header_max_loc[0] + header_w // 2
                        header_center_y = header_max_loc[1] + header_h // 2
                        scroll_y = header_center_y + 200
                        
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
                        pydirectinput.keyDown('shift')
                        pydirectinput.press('1')
                        pydirectinput.keyUp('shift')
                        time.sleep(0.5)
                        pydirectinput.press('space')
                        time.sleep(1.0)
        
        # Report any seeds not found
        if remaining_seeds:
            logger(f"⚠️ Could not find: {', '.join(remaining_seeds)}", "warning")
        
        # Close shop and return to garden
        logger("🚪 Closing shop...", "info")
        pydirectinput.press('esc')
        time.sleep(0.5)
        pydirectinput.press('esc')
        time.sleep(0.5)
        
        logger("🌱 Returning to garden...", "info")
        pydirectinput.keyDown('shift')
        time.sleep(0.2)
        pydirectinput.keyDown('2')
        time.sleep(0.2)
        pydirectinput.keyUp('2')
        pydirectinput.keyUp('shift')
        time.sleep(0.5)
        
        logger(f"✓ Auto-buy completed! Bought {seeds_bought} from {len(seeds_to_buy)} seed type(s).", "success")
        return seeds_bought > 0
        
    except Exception as e:
        logger(f"❌ Auto-buy error: {e}", "error")
        return False

def harvest_loop(logger=print):
    """
    Main automation loop that handles harvesting and/or auto-buy based on configuration.
    Supports three modes:
    1. Harvesting + Auto-Buy
    2. Harvesting only
    3. Auto-Buy only
    """
    
    # Validate configuration - at least one mode must be enabled
    if not Config.HARVESTING_ENABLED and not Config.AUTOBUY_ENABLED:
        logger("⚠️ ERROR: Both Harvesting and Auto-Buy are disabled!", "error")
        logger("⚠️ Please enable at least one mode in configuration.", "error")
        state.bot_running = False
        return
    
    # Initialize auto-buy timer if needed (start from configured interval)
    if Config.AUTOBUY_ENABLED and 'last_buy_time' not in state.stats:
        state.stats['last_buy_time'] = time.time()  # Start countdown from now
    
    # next_buy_time is now calculated directly in UI update loop for smooth countdown
    
    # Log active modes
    modes = []
    if Config.HARVESTING_ENABLED:
        modes.append("Harvesting")
    if Config.AUTOBUY_ENABLED:
        modes.append("Auto-Buy")
    logger(f"🤖 Bot running in mode: {' + '.join(modes)}", "info")
    
    # Main automation mode determines behavior
    if Config.HARVESTING_ENABLED:
        # --- HARVESTING MODE (with optional auto-buy) ---
        state.current_position['row'] = 0
        state.current_position['col'] = 0
        
        # BLOCK A: Update autobuy timer display (actual trigger happens during harvest loop)
        if Config.AUTOBUY_ENABLED and 'last_buy_time' in state.stats:
            state.stats['next_buy_time'] = max(0, Config.AUTOBUY_INTERVAL - (time.time() - state.stats['last_buy_time']))
        
        # BLOCK B: Harvest Logic (snake pattern)
        for row in range(Config.ROWS):
            if not state.bot_running:
                return
            
            state.current_position['row'] = row
            
            # Move right on even rows
            if row % 2 == 0:
                for col in range(Config.COLUMNS):
                    if not state.bot_running:
                        return
                    state.current_position['col'] = col
                    # Update autobuy timer and check if it's time to buy
                    if Config.AUTOBUY_ENABLED and 'last_buy_time' in state.stats:
                        time_remaining = Config.AUTOBUY_INTERVAL - (time.time() - state.stats['last_buy_time'])
                        state.stats['next_buy_time'] = max(0, time_remaining)
                        # Trigger autobuy mid-harvest when timer reaches zero
                        if time_remaining <= 0:
                            logger(f"⏰ Auto-buy timer reached - pausing harvest...", "warning")
                            if run_autobuy_routine(logger):
                                state.stats['last_buy_time'] = time.time()
                                state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                                logger("✓ Auto-buy complete. Resuming harvest...", "success")
                            else:
                                logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                                state.stats['last_buy_time'] = time.time()
                    harvest(logger)
                    if col < Config.COLUMNS - 1:
                        move('d', logger=logger)
            # Move left on odd rows
            else:
                for col in range(Config.COLUMNS - 1, -1, -1):
                    if not state.bot_running:
                        return
                    state.current_position['col'] = col
                    # Update autobuy timer and check if it's time to buy
                    if Config.AUTOBUY_ENABLED and 'last_buy_time' in state.stats:
                        time_remaining = Config.AUTOBUY_INTERVAL - (time.time() - state.stats['last_buy_time'])
                        state.stats['next_buy_time'] = max(0, time_remaining)
                        # Trigger autobuy mid-harvest when timer reaches zero
                        if time_remaining <= 0:
                            logger(f"⏰ Auto-buy timer reached - pausing harvest...", "warning")
                            if run_autobuy_routine(logger):
                                state.stats['last_buy_time'] = time.time()
                                state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                                logger("✓ Auto-buy complete. Resuming harvest...", "success")
                            else:
                                logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                                state.stats['last_buy_time'] = time.time()
                    harvest(logger)
                    if col > 0:
                        move('a', logger=logger)
            
            # Move down to the next row
            if row < Config.ROWS - 1:
                move('s', logger=logger)
        
        # Return to start after finishing the grid
        if state.bot_running:
            logger("✓ Grid finished. Returning to start...", "info")
            return_to_start(logger)
    
    else:
        # --- AUTO-BUY ONLY MODE (no harvesting) ---
        logger("🛒 Auto-buy only mode - waiting for next purchase cycle...", "info")
        
        while state.bot_running:
            current_time = time.time()
            time_remaining = Config.AUTOBUY_INTERVAL - (current_time - state.stats['last_buy_time'])
            
            # Update countdown timer for GUI
            state.stats['next_buy_time'] = max(0, time_remaining)
            
            # Check if it's time to buy
            if time_remaining <= 0:
                logger(f"⏰ Auto-buy timer reached ({Config.AUTOBUY_INTERVAL}s)", "warning")
                if run_autobuy_routine(logger):
                    state.stats['last_buy_time'] = current_time
                    state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                    logger("✓ Auto-buy complete. Waiting for next cycle...", "success")
                else:
                    logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                    # Reset last_buy_time to retry after interval (not hardcoded 30s)
                    state.stats['last_buy_time'] = current_time
            else:
                # Wait 1 second before checking again (keeps GUI timer updated)
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
    # logic: timestamp = now - (interval - 5)
    # elapsed = now - timestamp = interval - 5
    # remaining = interval - elapsed = 5
    if 'last_buy_time' not in state.stats:
        state.stats['last_buy_time'] = time.time() - (Config.AUTOBUY_INTERVAL - 5)
    
    while state.bot_running:
        current_time = time.time()
        elapsed = current_time - state.stats.get('last_buy_time', current_time)
        time_remaining = Config.AUTOBUY_INTERVAL - elapsed
        
        # Update countdown timer for GUI
        state.stats['next_buy_time'] = max(0, time_remaining)
        
        # Check if it's time to buy
        if time_remaining <= 0:
            logger(f"⏰ Auto-buy timer reached ({Config.AUTOBUY_INTERVAL}s)", "warning")
            if run_autobuy_routine(logger):
                state.stats['last_buy_time'] = time.time()
                state.stats['next_buy_time'] = Config.AUTOBUY_INTERVAL
                logger("✓ Auto-buy complete. Waiting for next cycle...", "success")
            else:
                logger(f"⚠️ Auto-buy failed, will retry in {Config.AUTOBUY_INTERVAL}s", "warning")
                # Reset last_buy_time to retry after interval
                state.stats['last_buy_time'] = time.time()
        else:
            # Just wait, do not move the character
            time.sleep(1)
    
    logger("🛒 Shop Mode stopped.", "info")
