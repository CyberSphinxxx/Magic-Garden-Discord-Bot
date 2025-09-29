# 🌱 Smart Garden Harvest Bot

An automated Python bot that harvests a 10x10 grid of plots in a snake pattern, automatically sells crops when inventory is full, and returns to the starting position.

## ✨ Features

- 🐍 **Snake Pattern Movement** - Efficiently harvests all plots in a back-and-forth pattern
- 📦 **Auto-Sell** - Detects when inventory is full and automatically sells crops
- 🔄 **Smart Return** - Intelligently returns to starting position after completing the grid
- ⚡ **Hotkey Integration** - Uses keyboard shortcuts for fast navigation
- 🔁 **Continuous Loop** - Runs indefinitely until manually stopped
- 📊 **Progress Tracking** - Shows cycle numbers and harvest counts

## 📋 Requirements

### Python Packages

```bash
pip install pyautogui opencv-python numpy pynput
```

### Required Files

- `inventory_full.png` - Screenshot of the "inventory full" popup

Place the image in the folder specified by `IMAGE_FOLDER` in the config (default: `images/`).

## 🎮 Game Controls

The bot uses these keyboard controls:
- **W/A/S/D** - Movement (up/left/down/right)
- **Spacebar** - Harvest crops
- **Shift+2** - Open Garden menu
- **Shift+3** - Open Sell menu

## ⚙️ Configuration

Edit these settings at the top of the script:

```python
GRID_SIZE = 10             # Size of the garden grid (10x10)
HARVEST_COUNT = 5          # Number of times to press space per plot
MOVE_DELAY = 0.15          # Delay between movement steps (seconds)
HARVEST_DELAY = 0.1        # Delay between harvest presses (seconds)
LOOP_COOLDOWN = 2          # Delay between full grid cycles (seconds)
CONFIDENCE = 0.8           # Image detection confidence (0.0-1.0)
DEBUG_MODE = True          # Enable debug messages
IMAGE_FOLDER = "images/"   # Folder containing screenshot images
```

## 🚀 Usage

1. **Setup**
   - Install required Python packages
   - Take a screenshot of the "inventory full" popup and save as `inventory_full.png`
   - Place the image in the `images/` folder (or update `IMAGE_FOLDER`)

2. **Run the Bot**
   ```bash
   python harvest_bot.py
   ```

3. **Switch to Game**
   - You have 3 seconds to switch to your game window
   - Make sure your character is at the top-left corner of the garden

4. **Stop the Bot**
   - Press `Ctrl+C` in the terminal to stop
   - The bot will show total cycles completed

## 📁 Project Structure

```
project/
├── MagicBot.py             # Main bot script
├── movement_test.py        # Test the bot path 10x10
├── images/                 # Screenshot folder
│   └── inventory_full.png  # Inventory full detection
└── README.md              # This file
```

## 🔧 How It Works

1. **Harvest Pattern**
   - Starts at top-left corner (0,0)
   - Even rows: moves left → right
   - Odd rows: moves right → left
   - Moves down after each row

2. **Inventory Management**
   - After each harvest, checks for "inventory full" popup
   - If detected, automatically:
     - Opens sell menu (Shift+3)
     - Sells all crops (Spacebar)
     - Returns to garden (Shift+2)

3. **Return to Start**
   - After completing the grid, moves back to (0,0)
   - Smart logic: only moves left if ended on right side
   - Repeats the cycle continuously

## ⚠️ Troubleshooting

**Bot not detecting inventory full popup:**
- Ensure `inventory_full.png` is a clear screenshot
- Try adjusting `CONFIDENCE` value (lower = more lenient)
- Check that the image is in the correct folder

**Movement is too fast/slow:**
- Adjust `MOVE_DELAY` for movement speed
- Adjust `HARVEST_DELAY` for harvest speed

**Bot clicks wrong location:**
- Make sure game window is in focus
- Verify hotkeys match your game settings

## 📝 Notes

- The bot requires the game window to be visible (not minimized)
- Resolution and UI scaling may affect image detection
- Always test in a safe environment first
- Keep the terminal window open to monitor progress

## 🛑 Disclaimer

This bot is for educational purposes. Use responsibly and in accordance with the game's terms of service.

---
