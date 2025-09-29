import pyautogui
import time
import cv2
import numpy as np
from pynput.keyboard import Controller, Key
from datetime import datetime
import sys

# =========================
# CONFIG
# =========================
GRID_SIZE = 10             # 10x10 plots
HARVEST_COUNT = 5          # How many times to press space per plot
DEBUG_MODE = True
CONFIDENCE = 0.8

MOVE_DELAY = 0.15          # delay for moving 1 step
HARVEST_DELAY = 0.1        # delay between harvest presses
LOOP_COOLDOWN = 2          # delay between full grid cycles
SELL_RETURN_DELAY = 1.0    # delay after returning from sell menu

# Image folder path (change this to your folder name)
IMAGE_FOLDER = "images/"   # e.g., "images/", "screenshots/", or "" for root

# Failsafe: Move mouse to corner to emergency stop
pyautogui.FAILSAFE = True

# Keyboard controller
keyboard = Controller()

# Statistics tracking
stats = {
    'total_harvests': 0,
    'total_sells': 0,
    'total_moves': 0,
    'start_time': None,
    'last_sell_time': None,
    'errors': 0,
    'inventory_checks': 0
}

# Current position tracking
current_position = {'row': 0, 'col': 0}

# =========================
# HELPER FUNCTIONS
# =========================

def locate_image(image, bottom_half=False, grayscale=True):
    """Locate image on screen (top or bottom half)."""
    try:
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width, screen_height // 2)
        if bottom_half:
            region = (0, screen_height // 2, screen_width, screen_height // 2)
        return pyautogui.locateOnScreen(
            image, 
            confidence=CONFIDENCE, 
            region=region,
            grayscale=grayscale  # Faster detection
        )
    except pyautogui.ImageNotFoundException:
        # Image not found - this is normal, not an error
        return None
    except Exception as e:
        # Only log actual errors (not normal "not found" cases)
        if DEBUG_MODE:
            print(f"⚠️ Unexpected image detection error: {e}")
        stats['errors'] += 1
        return None

def press_hotkey(key1, key2, delay=0.5):
    """Press a hotkey combination (e.g., Shift+2)."""
    try:
        keyboard.press(key1)
        keyboard.press(key2)
        time.sleep(0.05)
        keyboard.release(key2)
        keyboard.release(key1)
        time.sleep(delay)
    except Exception as e:
        print(f"⚠️ Hotkey error: {e}")
        stats['errors'] += 1

def check_inventory_full():
    """Check if inventory full popup appears."""
    stats['inventory_checks'] += 1
    found = locate_image(f"{IMAGE_FOLDER}inventory_full.png") is not None
    if found:
        print(f"📦 Inventory full detected at position ({current_position['row']}, {current_position['col']})")
    return found

def get_elapsed_time():
    """Get elapsed time since bot started."""
    if stats['start_time']:
        elapsed = time.time() - stats['start_time']
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return "00:00:00"

def get_harvests_per_hour():
    """Calculate harvests per hour."""
    if stats['start_time']:
        elapsed_hours = (time.time() - stats['start_time']) / 3600
        if elapsed_hours > 0:
            return stats['total_harvests'] / elapsed_hours
    return 0

def print_stats():
    """Print current statistics."""
    harvests_per_hour = get_harvests_per_hour()
    print(f"\n📊 STATISTICS")
    print(f"├─ Total Harvests: {stats['total_harvests']}")
    print(f"├─ Total Sells: {stats['total_sells']}")
    print(f"├─ Total Moves: {stats['total_moves']}")
    print(f"├─ Runtime: {get_elapsed_time()}")
    if stats['total_sells'] > 0:
        avg_harvests = stats['total_harvests'] / stats['total_sells']
        print(f"├─ Avg Harvests/Sell: {avg_harvests:.1f}")
    if harvests_per_hour > 0:
        print(f"├─ Harvests/Hour: {harvests_per_hour:.1f}")
    if stats['errors'] > 0:
        print(f"└─ Errors: {stats['errors']}")
    else:
        print(f"└─ No errors ✓")

def save_stats_to_file():
    """Save statistics to a log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("harvest_bot_stats.log", "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Session ended: {timestamp}\n")
            f.write(f"Total Harvests: {stats['total_harvests']}\n")
            f.write(f"Total Sells: {stats['total_sells']}\n")
            f.write(f"Total Moves: {stats['total_moves']}\n")
            f.write(f"Runtime: {get_elapsed_time()}\n")
            f.write(f"Harvests/Hour: {get_harvests_per_hour():.1f}\n")
            f.write(f"Errors: {stats['errors']}\n")
            f.write(f"{'='*60}\n")
        print(f"\n💾 Statistics saved to harvest_bot_stats.log")
    except Exception as e:
        print(f"⚠️ Could not save stats: {e}")

# =========================
# GAME ACTIONS
# =========================

def press_key(key, hold=0.05):
    """Press and release a key."""
    try:
        keyboard.press(key)
        time.sleep(hold)
        keyboard.release(key)
    except Exception as e:
        print(f"⚠️ Key press error: {e}")
        stats['errors'] += 1

def move(direction, steps=1):
    """Move in a direction for specified steps with inventory check."""
    for _ in range(steps):
        press_key(direction)
        stats['total_moves'] += 1
        
        # Update position tracking
        if direction == 'w':
            current_position['row'] -= 1
        elif direction == 's':
            current_position['row'] += 1
        elif direction == 'a':
            current_position['col'] -= 1
        elif direction == 'd':
            current_position['col'] += 1
        
        time.sleep(MOVE_DELAY)
        
        # Check inventory after every move
        if check_inventory_full():
            sell_crops()

def harvest():
    """Harvest current plot."""
    for _ in range(HARVEST_COUNT):
        press_key(Key.space)
        time.sleep(HARVEST_DELAY)
    stats['total_harvests'] += 1
    
    # Check inventory after harvesting
    if check_inventory_full():
        sell_crops()

def sell_crops():
    """Handle selling crops when inventory is full."""
    print(f"\n⚠️ INVENTORY FULL at position ({current_position['row']}, {current_position['col']})")
    stats['total_sells'] += 1
    stats['last_sell_time'] = time.time()
    
    # Store current position
    saved_position = current_position.copy()
    
    # Open sell menu (Shift+3)
    press_hotkey(Key.shift, '3')
    print("  ├─ Opening Sell menu...")
    
    # Press space to sell all
    press_key(Key.space)
    time.sleep(0.5)
    print("  ├─ Selling all crops...")
    
    # Return to garden (Shift+2)
    press_hotkey(Key.shift, '2')
    print("  └─ Returning to Garden...")
    time.sleep(SELL_RETURN_DELAY)
    
    # Restore position tracking
    current_position.update(saved_position)
    print(f"✅ Sale complete! Resuming at ({current_position['row']}, {current_position['col']})\n")

def return_to_start(last_row_index):
    """Smartly return to starting position based on where we ended."""
    print("🔄 Returning to start position...")
    
    # Move up to top row first
    move('w', GRID_SIZE - 1)
    
    # Only move left if last row was even (ended on right side)
    if last_row_index % 2 == 0:
        move('a', GRID_SIZE - 1)
    
    # Reset position tracking
    current_position['row'] = 0
    current_position['col'] = 0
    
    print("✅ Back at starting position!")

# =========================
# MAIN HARVEST LOOP
# =========================

def harvest_loop():
    """Main harvesting loop with snake pattern."""
    print("🌱 Starting snake harvest loop...")
    
    plots_harvested = 0
    
    # Reset position tracking
    current_position['row'] = 0
    current_position['col'] = 0
    
    for row in range(GRID_SIZE):
        current_position['row'] = row
        
        if row % 2 == 0:  # Even row → left to right
            for col in range(GRID_SIZE):
                current_position['col'] = col
                harvest()
                plots_harvested += 1
                
                # Move right if not at the end of the row
                if col < GRID_SIZE - 1:
                    move('d')
                    
        else:  # Odd row → right to left
            for col in range(GRID_SIZE - 1, -1, -1):
                current_position['col'] = col
                harvest()
                plots_harvested += 1
                
                # Move left if not at the start of the row
                if col > 0:
                    move('a')

        # Move down to next row (unless we're on the last row)
        if row < GRID_SIZE - 1:
            move('s')
    
    print(f"✅ Harvested {plots_harvested} plots this cycle")
    
    # Smart return to starting position
    return_to_start(GRID_SIZE - 1)

# =========================
# MAIN
# =========================

def main():
    """Main bot entry point."""
    print("=" * 60)
    print("🤖 SMART GARDEN HARVEST BOT v2.5")
    print("=" * 60)
    print(f"⚙️  Configuration:")
    print(f"   ├─ Grid Size: {GRID_SIZE}x{GRID_SIZE}")
    print(f"   ├─ Harvests per plot: {HARVEST_COUNT}")
    print(f"   ├─ Move Delay: {MOVE_DELAY}s")
    print(f"   ├─ Harvest Delay: {HARVEST_DELAY}s")
    print(f"   ├─ Loop Cooldown: {LOOP_COOLDOWN}s")
    print(f"   ├─ Sell Return Delay: {SELL_RETURN_DELAY}s")
    print(f"   ├─ Inventory Check: After every harvest & move")
    print(f"   └─ Debug Mode: {DEBUG_MODE}")
    print(f"\n💡 Tips:")
    print(f"   • Move mouse to top-left corner to emergency stop")
    print(f"   • Press Ctrl+C to stop gracefully")
    print(f"   • Make sure you're at top-left plot before starting")
    print(f"   • Stats will be saved to harvest_bot_stats.log")
    print("\n⏳ Bot starting in 3 seconds... Switch to game window!")
    
    for i in range(3, 0, -1):
        print(f"   {i}...", flush=True)
        time.sleep(1)
    
    print("\n🚀 Bot started!\n")
    stats['start_time'] = time.time()
    
    cycle = 0
    try:
        while True:
            cycle += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n{'='*60}")
            print(f"🔄 CYCLE #{cycle} | {timestamp}")
            print(f"{'='*60}")
            
            harvest_loop()
            
            print_stats()
            
            print(f"\n💤 Waiting {LOOP_COOLDOWN}s before next cycle...")
            time.sleep(LOOP_COOLDOWN)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("🛑 Bot stopped by user")
        print("="*60)
        print_stats()
        print(f"\n✅ Completed {cycle} full cycles")
        print(f"⏱️  Total Runtime: {get_elapsed_time()}")
        save_stats_to_file()
        print("\n🌱 Thank you for using Garden Harvest Bot!")
        print("="*60)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        print("Bot stopped due to error.")
        import traceback
        traceback.print_exc()
        print_stats()
        save_stats_to_file()
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")

if __name__ == "__main__":
    main()