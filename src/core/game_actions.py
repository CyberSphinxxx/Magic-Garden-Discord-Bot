import time
from pynput.keyboard import Key

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

def harvest_loop(logger=print):
    """Main harvesting loop that performs the snake pattern."""
    state.current_position['row'] = 0
    state.current_position['col'] = 0
    
    for row in range(Config.ROWS):
        if not state.bot_running: return
            
        state.current_position['row'] = row
        
        # Move right on even rows
        if row % 2 == 0:
            for col in range(Config.COLUMNS):
                if not state.bot_running: return
                state.current_position['col'] = col
                harvest(logger)
                if col < Config.COLUMNS - 1:
                    move('d', logger=logger)
        # Move left on odd rows
        else:
            for col in range(Config.COLUMNS - 1, -1, -1):
                if not state.bot_running: return
                state.current_position['col'] = col
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
