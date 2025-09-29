import pyautogui
import time
import cv2
import numpy as np
from pynput.keyboard import Controller, Key
from datetime import datetime

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
INVENTORY_CHECK_INTERVAL = 5  # Check inventory every N harvests (optimization)

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
    'start_time': None,
    'last_sell_time': None
}

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
    except Exception as e:
        if DEBUG_MODE:
            print(f"⚠️ Image detection error: {e}")
        return None

def press_hotkey(key1, key2, delay=0.5):
    """Press a hotkey combination (e.g., Shift+2)."""
    keyboard.press(key1)
    keyboard.press(key2)
    time.sleep(0.05)
    keyboard.release(key2)
    keyboard.release(key1)
    time.sleep(delay)

def check_inventory_full():
    """Check if inventory full popup appears."""
    found = locate_image(f"{IMAGE_FOLDER}inventory_full.png") is not None
    if found and DEBUG_MODE:
        print("📦 Inventory full detected!")
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

def print_stats():
    """Print current statistics."""
    print(f"\n📊 STATISTICS")
    print(f"├─ Total Harvests: {stats['total_harvests']}")
    print(f"├─ Total Sells: {stats['total_sells']}")
    print(f"├─ Runtime: {get_elapsed_time()}")
    if stats['total_sells'] > 0:
        avg_harvests = stats['total_harvests'] / stats['total_sells']
        print(f"└─ Avg Harvests/Sell: {avg_harvests:.1f}")

# =========================
# GAME ACTIONS
# =========================

def press_key(key, hold=0.05):
    """Press and release a key."""
    keyboard.press(key)
    time.sleep(hold)
    keyboard.release(key)

def move(direction, steps=1):
    """Move in a direction for specified steps."""
    for _ in range(steps):
        press_key(direction)
        time.sleep(MOVE_DELAY)

def harvest():
    """Harvest current plot."""
    for _ in range(HARVEST_COUNT):
        press_key(Key.space)
        time.sleep(HARVEST_DELAY)
    stats['total_harvests'] += 1

def sell_crops():
    """Handle selling crops when inventory is full."""
    print("⚠️ Inventory full! Selling crops...")
    stats['total_sells'] += 1
    stats['last_sell_time'] = time.time()
    
    # Open sell menu (Shift+3)
    press_hotkey(Key.shift, '3')
    if DEBUG_MODE:
        print("  ├─ Opened Sell menu")
    
    # Press space to sell all
    press_key(Key.space)
    time.sleep(0.5)
    if DEBUG_MODE:
        print("  ├─ Sold all crops")
    
    # Return to garden (Shift+2)
    press_hotkey(Key.shift, '2')
    if DEBUG_MODE:
        print("  └─ Returned to Garden")
    time.sleep(0.5)

def return_to_start(last_row_index):
    """Smartly return to starting position based on where we ended."""
    if DEBUG_MODE:
        print("🔄 Returning to start position...")
    
    # Move up to top row first
    move('w', GRID_SIZE - 1)
    
    # Only move left if last row was even (ended on right side)
    if last_row_index % 2 == 0:
        move('a', GRID_SIZE - 1)
    
    if DEBUG_MODE:
        print("✅ Back at starting position!")

# =========================
# MAIN HARVEST LOOP
# =========================

def harvest_loop():
    """Main harvesting loop with snake pattern."""
    if DEBUG_MODE:
        print("🌱 Starting snake harvest loop...")
    
    plots_harvested = 0
    harvest_counter = 0  # For optimized inventory checking
    
    for row in range(GRID_SIZE):
        if row % 2 == 0:  # Even row → left to right
            for col in range(GRID_SIZE):
                harvest()
                plots_harvested += 1
                harvest_counter += 1
                
                # Optimized: Check inventory every N harvests
                if harvest_counter >= INVENTORY_CHECK_INTERVAL:
                    if check_inventory_full():
                        sell_crops()
                    harvest_counter = 0
                
                # Move right if not at the end of the row
                if col < GRID_SIZE - 1:
                    move('d')
                    
        else:  # Odd row → right to left
            for col in range(GRID_SIZE):
                harvest()
                plots_harvested += 1
                harvest_counter += 1
                
                # Optimized: Check inventory every N harvests
                if harvest_counter >= INVENTORY_CHECK_INTERVAL:
                    if check_inventory_full():
                        sell_crops()
                    harvest_counter = 0
                
                # Move left if not at the end of the row
                if col < GRID_SIZE - 1:
                    move('a')

        # Move down to next row (unless we're on the last row)
        if row < GRID_SIZE - 1:
            move('s')
    
    # Final inventory check at end of cycle
    if check_inventory_full():
        sell_crops()
    
    if DEBUG_MODE:
        print(f"✅ Harvested {plots_harvested} plots this cycle")
    
    # Smart return to starting position
    return_to_start(GRID_SIZE - 1)

# =========================
# MAIN
# =========================

def main():
    """Main bot entry point."""
    print("=" * 60)
    print("🤖 SMART GARDEN HARVEST BOT v2.0")
    print("=" * 60)
    print(f"⚙️  Configuration:")
    print(f"   ├─ Grid Size: {GRID_SIZE}x{GRID_SIZE}")
    print(f"   ├─ Harvests per plot: {HARVEST_COUNT}")
    print(f"   ├─ Move Delay: {MOVE_DELAY}s")
    print(f"   ├─ Harvest Delay: {HARVEST_DELAY}s")
    print(f"   ├─ Loop Cooldown: {LOOP_COOLDOWN}s")
    print(f"   ├─ Inventory Check Interval: every {INVENTORY_CHECK_INTERVAL} harvests")
    print(f"   └─ Debug Mode: {DEBUG_MODE}")
    print(f"\n💡 Tips:")
    print(f"   • Move mouse to top-left corner to emergency stop")
    print(f"   • Press Ctrl+C to stop gracefully")
    print(f"   • Make sure you're at top-left plot before starting")
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
        print("\nThank you for using Garden Harvest Bot! 🌱")
        print("="*60)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        print("Bot stopped due to error.")     
        print_stats()

if __name__ == "__main__":
    main()