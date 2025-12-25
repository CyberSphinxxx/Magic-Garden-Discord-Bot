# Magic Garden Harvest Automation Bot

An automated Python bot with a beautiful GUI that harvests a 10x10 grid of plots in a snake pattern, automatically sells crops when inventory is full, and tracks comprehensive statistics in real-time.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

https://github.com/user-attachments/assets/ea63510f-dd4f-4a47-9695-d1426d6bec9a

## Important Notes for Windows Build

To achieve a portable-executable format, the application is packaged with PyInstaller into an EXE. Some antivirus engines (including Windows Defender) might report the packaged executable as a trojan, because PyInstaller has been used by others to package malicious Python code in the past. These reports can be safely ignored. If you absolutely do not trust the executable, you'll have to install Python yourself and run everything from source.

## Quick Start Guide (For Everyone!)

This is the easiest way to get the bot running, no programming skills required!

### Step 1: Download the Bot

1.  Go to the [**Releases Page**](https://github.com/CyberSphinxxx/Magic-Garden-Discord-Bot/releases) on the right side of this page.
2.  Under the latest release, find the **Assets** section.
3.  Download the `MagicGardenBot.exe` file.
4.  Place the executable in its own folder on your computer (recommended for organization).

> **Note:** If you don't see a Releases page, you can follow the [Advanced Setup Guide](#-advanced-setup-guide-for-users-who-want-to-run-the-code) to run the bot using Python.

### Step 2: Verify/Update the Auto-Sell Screenshot

The bot comes with a default `inventory_full.png` image located in the `src/images/` folder. This image helps the bot detect when your in-game inventory is full.

**Most users will NOT need to do this step.** The provided image should work for common game setups.

**However, if the bot isn't detecting your inventory correctly:**

1.  In the game, make your inventory full so the "Inventory Full" pop-up appears.
2.  Press **`Windows Key + Shift + S`** to open the Snipping Tool.
3.  Drag a box and capture **only the pop-up message**.
4.  Save this new screenshot as `inventory_full.png` inside the `src/images/` folder, overwriting the existing one.

This ensures the bot has the correct image for your specific game resolution and UI.

### Step 3: Run the Bot!

1.  Double-click `MagicGardenBot.exe` to start the bot.
2.  If Windows shows a security warning, click **"More info"** -> **"Run anyway"**. This is normal for new applications.
3.  Position your game character at the top-left plot of your garden.
4.  Click the big green **"START"** button in the bot's window.
5.  You have 3 seconds to switch back to your game window.

The bot will now start harvesting! You can monitor its progress in the GUI. To stop it, click the **"STOP"** button or move your mouse to the very top-left corner of your screen.

---

## Advanced Setup Guide (For Users Who Want to Run the Code)

If you want to run the Python script directly or modify the code, follow these steps.

### Step 1: Get the Code (Fork & Clone)

1.  **Fork the Repository**: Click the **"Fork"** button at the top-right of this page. This creates your own copy of the project under your GitHub account.
2.  **Clone Your Fork**: Click the green **"< > Code"** button on _your forked repository page_, copy the URL, and run the following command in your terminal (like Command Prompt or PowerShell):
    ```bash
    git clone <your-copied-url>
    ```
3.  Navigate into the new folder:
    ```bash
    cd Magic-Garden-Discord-Bot
    ```

### Step 2: Install Python

If you don't have Python, download the latest version from [python.org](https://www.python.org/downloads/). Make sure to check the box that says **"Add Python to PATH"** during installation.

### Step 3: Install Required Packages

Open your terminal in the project folder and run this command. It will automatically install all the necessary libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Bot

Refer to [Step 2 of the Quick Start Guide](#step-2-verifyupdate-the-auto-sell-screenshot) for instructions on how to verify or update the `inventory_full.png` screenshot, which is crucial for the bot's auto-sell feature.

### Step 5: Run the Bot

In your terminal, run the following command:

```bash
python main.py
```

The bot's GUI should appear, and you can start it just like in the Quick Start Guide.

---

## Features

### Core Functionality

- **Snake Pattern Harvesting** - Efficiently covers all 100 plots
- **Auto-Sell System** - Detects full inventory and sells automatically
- **Journal Interruption Handling** - Automatically handles journal pop-ups during gameplay
- **Smart Return** - Intelligently returns to starting position
- **Hotkey Integration** - Fast navigation using keyboard shortcuts
- **Continuous Loop** - Runs indefinitely until manually stopped

### GUI Features

- **Modern Dark Theme** - Discord-inspired, eye-friendly interface powered by CustomTkinter
- **Real-time Statistics** - Live metrics updated every 100ms
- **Mini Map** - Visual representation of current harvesting progress
- **Activity Log** - Color-coded messages with auto-scroll
- **Status Badge** - Dynamic colored indicator for running/idle states
- **Collapsible Sections** - Organized, clean interface with expandable panels
- **Built-in Guide** - Comprehensive help system with sidebar navigation
- **Tooltips** - Helpful hints on hover for all controls
- **Configurable Settings** - Adjust all parameters on-the-fly
- **Persistent Config** - Settings saved between sessions

---

## Configuration

All settings can be adjusted directly in the GUI. They are saved automatically in a `bot_config.json` file in your user home directory.

| Setting         | Description                                                           | Default |
| --------------- | --------------------------------------------------------------------- | ------- |
| `GRID_SIZE`     | Size of the garden grid (e.g., 10 for a 10x10 grid)                   | 10      |
| `HARVEST_COUNT` | How many times to press the harvest key on each plot                  | 5       |
| `MOVE_DELAY`    | Delay between each step (in seconds). Increase if movement is choppy. | 0.15    |
| `HARVEST_DELAY` | Delay between each harvest action (in seconds).                       | 0.1     |
| `LOOP_COOLDOWN` | How long to wait after completing a full harvest cycle (in seconds).  | 2       |

---

## Troubleshooting

- **Bot Not Detecting "Inventory Full"**:
  - Retake your `inventory_full.png` screenshot. Make sure it's a clear, tight crop of the pop-up.
  - Ensure the pop-up in-game looks exactly the same as it did when you took the screenshot.
- **Movement is Too Fast/Slow**:
  - Adjust the `MOVE_DELAY` and `HARVEST_DELAY` settings in the GUI.
  - Click "Save Config" to apply the changes.
- **Bot Stops Unexpectedly**:
  - Check the Activity Log in the GUI for any red error messages.
  - Make sure the game window remains the active, focused window.

---

## Disclaimer

This bot is for **educational purposes only**. Use it responsibly and in accordance with the game's terms of service. The developers are not responsible for any consequences resulting from its use.

## Contributing

Contributions, issues, and feature requests are welcome! If you're a developer, feel free to check out the developer-focused sections below.

---

## For Developers

### Project Structure

```
MAGIC-GARDEN-DISCORD-BOT/
├── .github/
│   └── workflows/
│       └── release.yml
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── automation.py      # Main harvesting loop logic
│   │   ├── config.py          # Configuration management
│   │   ├── game_actions.py    # Game interaction helpers
│   │   └── state.py           # Shared application state
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── collapsible_frame.py  # Expandable UI sections
│   │   ├── guide_window.py       # Built-in help/guide system
│   │   ├── main_window.py        # Main application window
│   │   ├── mini_map.py           # Visual grid progress indicator
│   │   ├── status_badge.py       # Dynamic status indicator
│   │   └── tooltip.py            # Hover tooltips component
│   ├── images/
│   │   ├── garden_button.png
│   │   ├── go_to_journal.png
│   │   ├── harvest_button.png
│   │   ├── inventory_full.png
│   │   ├── log_new_items_in_journal.png
│   │   ├── sell_all_button.png
│   │   └── sell_button.png
│   ├── bot_icon.ico
│   └── version.txt
├── main.py                    # Application entry point
├── .gitignore
├── LICENSE
├── MagicGardenBot.spec        # PyInstaller build spec
├── README.md
└── requirements.txt
```

### Dependencies

| Package         | Purpose                              |
| --------------- | ------------------------------------ |
| `pyautogui`     | Mouse/keyboard automation            |
| `opencv-python` | Image recognition for screen detection |
| `numpy`         | Array operations for image processing |
| `pynput`        | Keyboard/mouse input monitoring      |
| `customtkinter` | Modern themed Tkinter GUI            |

### Building the Executable

If you want to bundle the application into a `.exe` file yourself, you'll need `pyinstaller`.

1.  **Install PyInstaller**:
    ```bash
    pip install pyinstaller
    ```
2.  **Build the Executable**:
    Run this command from the root folder of the project:
    ```bash
    pyinstaller --onefile --windowed --icon=src/bot_icon.ico --add-data "src/images;images" --name="MagicGardenBot" main.py
    ```
    The final `.exe` will be located in the `dist` folder.

---

Happy Harvesting!
