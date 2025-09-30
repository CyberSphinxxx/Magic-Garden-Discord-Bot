#  Magic Garden Bot

An automated Python bot with a beautiful GUI that harvests a 10x10 grid of plots in a snake pattern, automatically sells crops when inventory is full, and tracks comprehensive statistics in real-time.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

##  Features

###  Core Functionality
-  **Snake Pattern Harvesting** - Efficiently covers all 100 plots
-  **Auto-Sell System** - Detects full inventory and sells automatically
-  **Smart Return** - Intelligently returns to starting position
-  **Hotkey Integration** - Fast navigation using keyboard shortcuts
-  **Continuous Loop** - Runs indefinitely until manually stopped

###  GUI Features
-  **Beautiful Dark Theme** - Modern, eye-friendly interface
-  **Real-time Statistics** - 9 live metrics updated every 100ms
-  **Activity Log** - Color-coded messages with auto-scroll
-  **Configurable Settings** - Adjust all parameters on-the-fly
-  **Persistent Config** - Settings saved between sessions
-  **Visual Status Indicators** - Clear running/idle states

###  Statistics Tracked
- Cycles completed
- Total harvests
- Total sells
- Total moves
- Harvests per hour
- Runtime
- Current position (row, col)
- Errors count
- Bot status

##  Requirements

### Python Packages

```bash
pip install pyautogui opencv-python numpy pynput
```

### Required Files

Place in the `src/images/` folder:
- `inventory_full.png` - Screenshot of the "inventory full" popup

##  Game Controls

The bot uses these keyboard controls:
- **W/A/S/D** - Movement (up/left/down/right)
- **Spacebar** - Harvest crops
- **Shift+2** - Open Garden menu
- **Shift+3** - Open Sell menu

## 📁 Project Structure

```
MAGIC-GARDEN-DISCORD-BOT/
├── src/
│   ├── images/
│   │   ├── inventory_full.png     # Required screenshot
│   │   └── bot_icon.ico           # Bot icon
│   ├── MagicGardenBot.py          # GUI version
│   ├── movement_test.py           # Movement testing script
│   ├── bot_config.json            # Auto-generated config
│   └── harvest_bot_stats.log      # Auto-generated logs
├── build/                         # PyInstaller build files
├── dist/
│   └── MagicGardenBot.exe        # Executable file
├── MagicGardenBot.spec           # PyInstaller spec file
└── README.md                      # This file
```

## ⚙️ Configuration

All settings can be adjusted in the GUI or edited in `bot_config.json`:

```json
{
    "GRID_SIZE": 10,
    "HARVEST_COUNT": 5,
    "MOVE_DELAY": 0.15,
    "HARVEST_DELAY": 0.1,
    "LOOP_COOLDOWN": 2,
    "SELL_RETURN_DELAY": 1.0,
    "IMAGE_FOLDER": "images/"
}
```

### Configuration Options

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `GRID_SIZE` | Size of the garden grid | 10 | 1-20 |
| `HARVEST_COUNT` | Times to press space per plot | 5 | 1-10 |
| `MOVE_DELAY` | Delay between movements (s) | 0.15 | 0.05-1.0 |
| `HARVEST_DELAY` | Delay between harvests (s) | 0.1 | 0.05-1.0 |
| `LOOP_COOLDOWN` | Delay between cycles (s) | 2 | 0-10 |
| `SELL_RETURN_DELAY` | Delay after selling (s) | 1.0 | 0.5-3.0 |

##  Usage

### Running the Python Script

1. **Setup**
   ```bash
   cd src
   python MagicGardenBot.py
   ```

2. **Configure Settings**
   - Adjust parameters in the Configuration panel
   - Click "💾 Save Config"

3. **Start Bot**
   - Position your character at the top-left plot
   - Click "▶ START"
   - Switch to game window within 3 seconds

4. **Monitor**
   - Watch real-time statistics update
   - View activity log for events
   - Track position and performance

5. **Stop Bot**
   - Click "⏹ STOP" button
   - Or press `Ctrl+C` in terminal
   - Or move mouse to top-left corner (emergency stop)

### Running the Executable

1. **Navigate to dist folder**
   ```bash
   cd dist
   ```

2. **Double-click** `MagicGardenBot.exe`

3. **First Run** - Windows may show a warning:
   - Click "More info"
   - Click "Run anyway"
   - This is normal for PyInstaller applications

##  How It Works

### Harvest Pattern

```
Start → → → → → → → → → End
  ↓                       ↓
  ← ← ← ← ← ← ← ← ← ← ←
  ↓                       ↓
  → → → → → → → → → → →
  ↓                       ↓
  ... (continues snake pattern)
  ↓
Return to Start
```

1. Starts at position (0,0) - top-left
2. Even rows: moves left → right
3. Odd rows: moves right → left
4. Moves down after each row
5. Returns to start using smart pathing

### Inventory Management

1. Checks inventory after **every harvest**
2. Checks inventory after **every movement**
3. When full:
   - Opens sell menu (Shift+3)
   - Sells all crops (Spacebar)
   - Returns to garden (Shift+2)
   - Resumes at exact position

### Position Tracking

- Tracks current (row, col) in real-time
- Shows position in GUI statistics
- Preserves position after selling
- Logs position during important events

##  Building the Executable

### Prerequisites

```bash
pip install pyinstaller
```

### Build Command

```bash
pyinstaller --onefile --windowed --icon=src/images/bot_icon.ico --name="MagicGardenBot" src/MagicGardenBot.py
```

### Build Options

- `--onefile` - Single executable file
- `--windowed` - No console window (GUI only)
- `--icon` - Custom icon file (.ico)
- `--name` - Output filename

### Using Spec File

For advanced builds, use `MagicGardenBot.spec`:

```bash
pyinstaller MagicGardenBot.spec
```

The spec file includes:
- Image folder bundling
- Optimized compression (UPX)
- Hidden imports handling
- Better error handling

## 📸 Taking Screenshots

### For `inventory_full.png`:

1. **Trigger the popup** in-game
2. **Press** `Windows + Shift + S` (Snipping Tool)
3. **Select** just the "inventory full" popup
4. **Save** as `inventory_full.png` in `src/images/`

**Tips:**
- Capture only the popup, not the whole screen
- Use clear, high-contrast image
- Test different confidence levels if detection fails

## ⚠️ Troubleshooting

### Bot not detecting inventory full popup

**Solutions:**
- Retake screenshot with better quality
- Lower `CONFIDENCE` value (0.6-0.7)
- Ensure popup is fully visible when captured
- Check image is in correct folder

### Movement is too fast/slow

**Solutions:**
- Adjust `MOVE_DELAY` in config panel
- Adjust `HARVEST_DELAY` for harvest speed
- Save config after changes

### Bot stops unexpectedly

**Solutions:**
- Check Activity Log for errors
- Ensure game window stays in focus
- Verify hotkeys match game settings
- Check internet connection (if needed)

### Executable won't run

**Solutions:**
- Click "More info" → "Run anyway" on Windows Defender
- Rebuild with `--debug` flag for error messages
- Ensure all dependencies are installed
- Run as administrator if needed

## 💡 Tips & Best Practices

- ✅ Always start at the top-left plot (0,0)
- ✅ Keep game window visible (not minimized)
- ✅ Test with small `GRID_SIZE` first
- ✅ Monitor first few cycles to ensure proper operation
- ✅ Keep Activity Log visible to catch issues early
- ✅ Adjust delays based on your PC's performance
- ✅ Use the Reset Stats button to start fresh tracking

##  Safety Features

-  **Failsafe Mode** - Move mouse to corner to stop
-  **Error Tracking** - Counts and logs all errors
-  **Position Preservation** - Never loses place after selling
-  **Graceful Shutdown** - Stats saved on exit
-  **Confirmation Dialogs** - Prevents accidental resets

##  Performance

Expected performance on modern hardware:
- **~600-700 harvests/hour** (10x10 grid, 5 harvests per plot)
- **~10-15 sells/hour** (depending on inventory size)
- **~200-300 moves/hour**
- **99%+ success rate** (with proper configuration)

## 📝 Logs

### Activity Log (GUI)
- Real-time events with timestamps
- Color-coded messages:
  - 🔵 **Blue** - Info
  - 🟢 **Green** - Success
  - 🟡 **Yellow** - Warning
  - 🔴 **Red** - Error

### Statistics Log (File)
Saved to `harvest_bot_stats.log`:
- Session timestamps
- Total harvests
- Total sells
- Runtime duration
- Harvests per hour
- Error count


## 🛑 Disclaimer

This bot is for **educational purposes only**. Use responsibly and in accordance with the game's terms of service. The developers are not responsible for any consequences resulting from the use of this software.


## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 💬 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Review the Activity Log for errors
3. Ensure all requirements are met
4. Verify your configuration settings

---

**Made with ❤️ for automated farming**

🌱 Happy Harvesting! 🌱
