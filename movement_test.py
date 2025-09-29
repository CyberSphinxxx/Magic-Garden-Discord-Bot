import time
from pynput.keyboard import Controller

# CONFIG
GRID_SIZE = 10
MOVE_DELAY = 0.15

keyboard = Controller()

def press_key(key, hold=0.05):
    keyboard.press(key)
    time.sleep(hold)
    keyboard.release(key)

def move(direction, steps=1):
    for _ in range(steps):
        press_key(direction)
        time.sleep(MOVE_DELAY)

def movement_test():
    print("🚶 Starting snake movement test...")

    for row in range(GRID_SIZE):
        if row % 2 == 0:  # even row → left to right
            for col in range(GRID_SIZE - 1):
                move('d')
        else:  # odd row → right to left
            for col in range(GRID_SIZE - 1):
                move('a')

        if row < GRID_SIZE - 1:
            move('s')

    # Return to top-left
    print("🔄 Returning to start position...")
    
    # Check if last row was odd (ended on left) or even (ended on right)
    last_row = GRID_SIZE - 1
    if last_row % 2 == 0:  # ended on right side
        move('a', GRID_SIZE - 1)  # move left first
        move('w', GRID_SIZE - 1)  # then up
    else:  # ended on left side
        move('w', GRID_SIZE - 1)  # just move up (already on left)
    
    print("✅ Path complete and back at starting position!")

print("Test starting in 3 seconds... Switch to game window!")
time.sleep(3)
movement_test()