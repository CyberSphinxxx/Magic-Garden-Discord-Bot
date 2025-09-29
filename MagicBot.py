import pyautogui
import time
import cv2
import numpy as np
from pynput.keyboard import Controller, Key

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

# Keyboard controller
keyboard = Controller()

# =========================
# HELPER FUNCTIONS
# =========================

def locate_image(image, bottom_half=False):
    """Locate image on screen (top or bottom half)."""
    try:
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width, screen_height // 2)
        if bottom_half:
            region = (0, screen_height // 2, screen_width, screen_height // 2)
        return pyautogui.locateOnScreen(image, confidence=CONFIDENCE, region=region)
    except:
        return None

def click_button(image, bottom_half=False, retries=3):
    """Click a button by its screenshot."""
    for _ in range(retries):
        box = locate_image(image, bottom_half=bottom_half)
        if box:
            pyautogui.click(pyautogui.center(box))
            time.sleep(1)
            return True
        time.sleep(0.5)
    if DEBUG_MODE:
        print(f"⚠️ Could not find: {image}")
    return False

def check_inventory_full():
    """Check if inventory full popup appears."""
    return locate_image("inventory_full.png") is not None

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

def sell_crops():
    """Handle selling crops when inventory is full."""
    print("⚠️ Inventory full! Selling crops...")
    if click_button("sell_button.png"):
        print("✅ Sell button clicked")
        time.sleep(0.5)
        if click_button("sell_all_button.png", bottom_half=True):
            print("✅ Sell All clicked")
            time.sleep(1)
        if click_button("garden_button.png"):
            print("✅ Returned to Garden")
            time.sleep(0.5)

def return_to_start(last_row_index):
    """Smartly return to starting position based on where we ended."""
    print("🔄 Returning to start position...")
    
    # Move up to top row first
    move('w', GRID_SIZE - 1)
    
    # Only move left if last row was even (ended on right side)
    if last_row_index % 2 == 0:
        move('a', GRID_SIZE - 1)
    
    print("✅ Back at starting position!")

# =========================
# MAIN HARVEST LOOP
# =========================

def harvest_loop():
    print("🌱 Starting snake harvest loop...")
    plots_harvested = 0
    
    for row in range(GRID_SIZE):
        if row % 2 == 0:  # Even row → left to right
            for col in range(GRID_SIZE):
                harvest()
                plots_harvested += 1
                
                # Check for full inventory after each harvest
                if check_inventory_full():
                    sell_crops()
                
                # Move right if not at the end of the row
                if col < GRID_SIZE - 1:
                    move('d')
                    
        else:  # Odd row → right to left
            for col in range(GRID_SIZE):
                harvest()
                plots_harvested += 1
                
                # Check for full inventory after each harvest
                if check_inventory_full():
                    sell_crops()
                
                # Move left if not at the end of the row
                if col < GRID_SIZE - 1:
                    move('a')

        # Move down to next row (unless we're on the last row)
        if row < GRID_SIZE - 1:
            move('s')
    
    print(f"✅ Harvested {plots_harvested} plots")
    
    # Smart return to starting position
    return_to_start(GRID_SIZE - 1)

# =========================
# MAIN
# =========================

def main():
    print("=" * 50)
    print("🤖 SMART GARDEN HARVEST BOT")
    print("=" * 50)
    print(f"Grid Size: {GRID_SIZE}x{GRID_SIZE}")
    print(f"Harvests per plot: {HARVEST_COUNT}")
    print(f"Debug Mode: {DEBUG_MODE}")
    print("\nBot starting in 3 seconds... Switch to game window!")
    time.sleep(3)
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"🔄 CYCLE #{cycle}")
            print(f"{'='*50}")
            
            harvest_loop()
            
            print(f"\n💤 Waiting {LOOP_COOLDOWN}s before next cycle...")
            time.sleep(LOOP_COOLDOWN)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        print(f"Total cycles completed: {cycle}")

if __name__ == "__main__":
    main()