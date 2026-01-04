# Magic Garden Harvest Automation Bot

An automated Python bot with a beautiful GUI that harvests a 10x10 grid of plots in a snake pattern, automatically sells crops when inventory is full, and tracks comprehensive statistics in real-time.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

[https://github.com/user-attachments/assets/ea63510f-dd4f-4a47-9695-d1426d6bec9a](https://github.com/user-attachments/assets/ea63510f-dd4f-4a47-9695-d1426d6bec9a)


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

## Important Notes for Windows Build

- To achieve a portable-executable format, the application is packaged with **PyInstaller** into an EXE.
- Some antivirus engines (including Windows Defender) might report the packaged executable as a trojan, because PyInstaller has been used by others to package malicious Python code in the past. 
- These reports can be safely ignored. If you absolutely do not trust the executable, you'll have to install Python yourself and run everything from source.

## Quick Start Guide (For Non-Programmers)

This is the easiest way to get the bot running, no programming skills required!

### Step 1: Download the Bot

1.  Go to the [**Releases Page**](https://github.com/CyberSphinxxx/Magic-Garden-Discord-Bot/releases) on the right side of this page.
2.  Under the latest release, find the **Assets** section.
3.  Download the `MagicGardenBot.exe` file.
4.  Place the executable in its own folder on your computer.

> **Note:** If you don't see a Releases page, you can follow the [Advanced Setup Guide](#-advanced-setup-guide-for-users-who-want-to-run-the-code) to run the bot using Python.

### Step 2: Run the Bot!

1.  Double-click `MagicGardenBot.exe` to start the bot.
2.  If Windows shows a security warning, click **"More info"** -> **"Run anyway"**. This is normal for new applications.
3.  Position your game character at the top-left plot of your garden.
4.  Click the big green **"START"** button in the bot's window.
5.  You have 3 seconds to switch back to your game window.

The bot will now start harvesting! You can monitor its progress in the GUI.

---

## Frequently Asked Questions (FAQ) & Troubleshooting

### CRITICAL: Download the correct file!

**Do not download "Source code (zip)"** unless you are a developer installed with Python.
* **Correct:** Download `MagicGardenBot.exe` from the **Assets** section of the latest Release.
* **Incorrect:** Downloading the zip file will only give you the raw code, which won't run without installing Python and dependencies manually.

### The bot keeps harvesting when inventory is full!
If the bot doesn't sell automatically, it means the image recognition failed to see the "Inventory Full" popup.

**1. Check Display Scale (Most Common Fix)**

OpenCV reads pixels exactly as they appear on your screen. If your display is zoomed in, the images won't match.
* Go to **Windows Settings > System > Display**.
* Ensure **Scale and layout** is set to **100%**.

**2. Update the Reference Image**

You don't have to change the screenshot as this is already working, unless the game had an update where they change the color or font of the said notification.

* Wait for the "Inventory Full" popup to appear.
* Use `Win + Shift + S` to take a screenshot of **only the popup text/box**.
* Save it as `inventory_full.png` and replace the file in `src/images/` (if running from source) or ensure the bot is using your local config if applicable.

### The bot moves too fast / misses crops
If your internet connection or PC lags, the bot might move before the game registers the harvest.
* Open the Bot GUI.
* Increase **MOVE_DELAY** (e.g., to `0.25`) and **HARVEST_DELAY**.

### Can I run this in the background?
- **No.** The game window must be **visible** and **active** on your screen. You cannot minimize it or cover it with other windows, as the bot needs to "see" the pixels to make decisions.
- **Important:** You also **cannot use your computer for other tasks** while the bot is running. Since the bot simulates actual keystrokes and mouse clicks, it requires full control of your input devices. If you try to type in another window or move the mouse, the bot will lose focus and fail.

### Does it work on a second monitor?
**Yes.** However, ensure:
1. The scaling on the second monitor is also set to **100%**.
2. The game window is fully visible on that monitor.

### Why isn't the bot moving/harvesting?
**You must click the Game Window!**
The bot simulates real keyboard presses. If your game window isn't "focused" (active), the keystrokes will go nowhere.
* **Procedure:** When you click **START**, you have a 3-second countdown. You **must** click on your game window immediately during this countdown so it is the active window when the bot starts.

**How to Test:**
If you aren't sure if it's working, open a blank **Notepad** file.
1. Click **START** on the bot.
2. Quickly click into the Notepad window.
3. If the bot is working, you will see it typing `d`, `d`, `d`, `d`, `s`, `s`, `s` and so on into the Notepad.

### Bot Stops Unexpectedly
* Check the **Activity Log** in the GUI for any red error messages.
* Make sure the game window remains the active, focused window at all times.

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

Refer to the [FAQ Section above](#-the-bot-keeps-harvesting-when-inventory-is-full) for instructions on how to verify or update the `inventory_full.png` screenshot if the bot fails to detect your inventory state.

### Step 5: Run the Bot

In your terminal, run the following command:

```bash
python main.py
```

The bot's GUI should appear, and you can start it just like in the Quick Start Guide.

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
│   │   ├── automation.py       # Main harvesting loop logic
│   │   ├── config.py           # Configuration management
│   │   ├── game_actions.py     # Game interaction helpers
│   │   └── state.py            # Shared application state
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
├── main.py                     # Application entry point
├── .gitignore
├── LICENSE
├── MagicGardenBot.spec         # PyInstaller build spec
├── README.md
└── requirements.txt
```

### Dependencies

| Package         | Purpose                                |
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

## Disclaimer

This bot is for **educational purposes only**. Use it responsibly and in accordance with the game's terms of service. The developers are not responsible for any consequences resulting from its use.

## Contributing

Contributions, issues, and feature requests are welcome!.

---

Happy Harvesting!


