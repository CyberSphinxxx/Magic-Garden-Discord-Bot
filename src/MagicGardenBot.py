import pyautogui
import time
import cv2
import numpy as np
from pynput.keyboard import Controller, Key
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os

# =========================
# CONFIG
# =========================
class Config:
    GRID_SIZE = 10
    HARVEST_COUNT = 5
    CONFIDENCE = 0.8
    MOVE_DELAY = 0.15
    HARVEST_DELAY = 0.1
    LOOP_COOLDOWN = 2
    SELL_RETURN_DELAY = 1.0
    IMAGE_FOLDER = "src/images/"
    
    @classmethod
    def save(cls):
        """Save config to file."""
        config_dict = {
            'GRID_SIZE': cls.GRID_SIZE,
            'HARVEST_COUNT': cls.HARVEST_COUNT,
            'MOVE_DELAY': cls.MOVE_DELAY,
            'HARVEST_DELAY': cls.HARVEST_DELAY,
            'LOOP_COOLDOWN': cls.LOOP_COOLDOWN,
            'SELL_RETURN_DELAY': cls.SELL_RETURN_DELAY,
            'IMAGE_FOLDER': cls.IMAGE_FOLDER,
        }
        with open('bot_config.json', 'w') as f:
            json.dump(config_dict, f, indent=4)
    
    @classmethod
    def load(cls):
        """Load config from file."""
        try:
            if os.path.exists('bot_config.json'):
                with open('bot_config.json', 'r') as f:
                    config_dict = json.load(f)
                    for key, value in config_dict.items():
                        setattr(cls, key, value)
        except Exception as e:
            print(f"Could not load config: {e}")

# Failsafe
pyautogui.FAILSAFE = True

# Keyboard controller
keyboard = Controller()

# Statistics
stats = {
    'total_harvests': 0,
    'total_sells': 0,
    'total_moves': 0,
    'start_time': None,
    'last_sell_time': None,
    'errors': 0,
    'inventory_checks': 0,
    'cycles': 0
}

# Position tracking
current_position = {'row': 0, 'col': 0}

# Bot state
bot_running = False
bot_paused = False

# =========================
# HELPER FUNCTIONS
# =========================

def locate_image(image, bottom_half=False, grayscale=True):
    """Locate image on screen."""
    try:
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width, screen_height // 2)
        if bottom_half:
            region = (0, screen_height // 2, screen_width, screen_height // 2)
        return pyautogui.locateOnScreen(
            image, 
            confidence=Config.CONFIDENCE, 
            region=region,
            grayscale=grayscale
        )
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        stats['errors'] += 1
        return None

def press_hotkey(key1, key2, delay=0.5):
    """Press a hotkey combination."""
    try:
        keyboard.press(key1)
        keyboard.press(key2)
        time.sleep(0.05)
        keyboard.release(key2)
        keyboard.release(key1)
        time.sleep(delay)
    except Exception as e:
        stats['errors'] += 1

def check_inventory_full():
    """Check if inventory full popup appears."""
    stats['inventory_checks'] += 1
    found = locate_image(f"{Config.IMAGE_FOLDER}inventory_full.png") is not None
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
        stats['errors'] += 1

def move(direction, steps=1):
    """Move in a direction with inventory check."""
    for _ in range(steps):
        if not bot_running:
            return
        
        press_key(direction)
        stats['total_moves'] += 1
        
        if direction == 'w':
            current_position['row'] -= 1
        elif direction == 's':
            current_position['row'] += 1
        elif direction == 'a':
            current_position['col'] -= 1
        elif direction == 'd':
            current_position['col'] += 1
        
        time.sleep(Config.MOVE_DELAY)
        
        if check_inventory_full():
            sell_crops()

def harvest():
    """Harvest current plot."""
    for _ in range(Config.HARVEST_COUNT):
        if not bot_running:
            return
        press_key(Key.space)
        time.sleep(Config.HARVEST_DELAY)
    stats['total_harvests'] += 1
    
    if check_inventory_full():
        sell_crops()

def sell_crops():
    """Handle selling crops when inventory is full."""
    stats['total_sells'] += 1
    stats['last_sell_time'] = time.time()
    
    # Log to GUI if available
    if 'app' in globals():
        app.log(f"📦 Inventory full at ({current_position['row']}, {current_position['col']}) - Selling...", "warning")
    
    saved_position = current_position.copy()
    
    press_hotkey(Key.shift, '3')
    time.sleep(0.3)
    press_key(Key.space)
    time.sleep(0.5)
    press_hotkey(Key.shift, '2')
    time.sleep(Config.SELL_RETURN_DELAY)
    
    current_position.update(saved_position)
    
    if 'app' in globals():
        app.log("✓ Crops sold! Resuming harvest...", "success")

def return_to_start(last_row_index):
    """Return to starting position."""
    move('w', Config.GRID_SIZE - 1)
    
    if last_row_index % 2 == 0:
        move('a', Config.GRID_SIZE - 1)
    
    current_position['row'] = 0
    current_position['col'] = 0

def harvest_loop():
    """Main harvesting loop."""
    current_position['row'] = 0
    current_position['col'] = 0
    
    for row in range(Config.GRID_SIZE):
        if not bot_running:
            return
            
        current_position['row'] = row
        
        if row % 2 == 0:
            for col in range(Config.GRID_SIZE):
                if not bot_running:
                    return
                current_position['col'] = col
                harvest()
                if col < Config.GRID_SIZE - 1:
                    move('d')
        else:
            for col in range(Config.GRID_SIZE - 1, -1, -1):
                if not bot_running:
                    return
                current_position['col'] = col
                harvest()
                if col > 0:
                    move('a')

        if row < Config.GRID_SIZE - 1:
            move('s')
    
    return_to_start(Config.GRID_SIZE - 1)

# =========================
# GUI APPLICATION
# =========================

class HarvestBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 Magic Garden Bot")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # Load config
        Config.load()
        
        # Style
        self.setup_style()
        
        # Main container with left and right sections
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (controls, stats, config)
        left_panel = tk.Frame(main_container, bg=self.colors['bg_dark'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(10, 5))
        
        # Right panel (activity log)
        right_panel = tk.Frame(main_container, bg=self.colors['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10))
        
        # Create UI in panels
        self.create_header(left_panel)
        self.create_control_panel(left_panel)
        self.create_stats_panel(left_panel)
        self.create_config_panel(left_panel)
        self.create_log_panel(right_panel)
        self.create_footer()
        
        # Update loop
        self.update_ui()
        
    def setup_style(self):
        """Setup custom styling."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_dark = "#1e1e2e"
        bg_medium = "#2a2a3e"
        bg_light = "#363650"
        accent = "#89b4fa"
        success = "#a6e3a1"
        warning = "#fab387"
        error = "#f38ba8"
        text = "#cdd6f4"
        
        # Configure styles
        style.configure("TFrame", background=bg_dark)
        style.configure("Header.TLabel", background=bg_dark, foreground=accent, 
                       font=("Segoe UI", 20, "bold"))
        style.configure("Title.TLabel", background=bg_medium, foreground=text, 
                       font=("Segoe UI", 11, "bold"))
        style.configure("Stats.TLabel", background=bg_medium, foreground=text, 
                       font=("Segoe UI", 10))
        style.configure("TLabel", background=bg_dark, foreground=text, 
                       font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        
        self.root.configure(bg=bg_dark)
        self.colors = {
            'bg_dark': bg_dark,
            'bg_medium': bg_medium,
            'bg_light': bg_light,
            'accent': accent,
            'success': success,
            'warning': warning,
            'error': error,
            'text': text
        }
        
    def create_header(self, parent):
        """Create header section."""
        header_frame = tk.Frame(parent, bg=self.colors['bg_dark'], height=60)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        title = ttk.Label(header_frame, text="🌱 Smart Garden Harvest Bot", 
                         style="Header.TLabel")
        title.pack(side=tk.LEFT)
        
        version = ttk.Label(header_frame, text="v2.0 GUI Edition", 
                           style="TLabel")
        version.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_control_panel(self, parent):
        """Create control buttons."""
        control_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(control_frame, text="▶ START", 
                                      command=self.start_bot,
                                      bg=self.colors['success'], fg="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=12, height=2,
                                      cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=3)
        
        self.stop_button = tk.Button(control_frame, text="⏹ STOP", 
                                     command=self.stop_bot,
                                     bg=self.colors['error'], fg="black",
                                     font=("Segoe UI", 11, "bold"),
                                     width=12, height=2,
                                     state=tk.DISABLED,
                                     cursor="hand2")
        self.stop_button.pack(side=tk.LEFT, padx=3)
        
        self.reset_button = tk.Button(control_frame, text="🔄 RESET", 
                                      command=self.reset_stats,
                                      bg=self.colors['warning'], fg="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=12, height=2,
                                      cursor="hand2")
        self.reset_button.pack(side=tk.LEFT, padx=3)
        
        # Status below buttons
        status_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="● IDLE", 
                                     bg=self.colors['bg_dark'],
                                     fg=self.colors['text'],
                                     font=("Segoe UI", 12, "bold"))
        self.status_label.pack()
        
    def create_stats_panel(self, parent):
        """Create statistics panel."""
        stats_frame = tk.LabelFrame(parent, text="📊 Statistics", 
                                   bg=self.colors['bg_medium'],
                                   fg=self.colors['accent'],
                                   font=("Segoe UI", 11, "bold"),
                                   padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Create stats grid
        stats_grid = tk.Frame(stats_frame, bg=self.colors['bg_medium'])
        stats_grid.pack(fill=tk.X)
        
        self.stat_labels = {}
        stats_config = [
            ("Cycles", "cycles", 0, 0),
            ("Total Harvests", "total_harvests", 0, 1),
            ("Total Sells", "total_sells", 0, 2),
            ("Total Moves", "total_moves", 1, 0),
            ("Harvests/Hour", "rate", 1, 1),
            ("Runtime", "runtime", 1, 2),
            ("Position", "position", 2, 0),
            ("Errors", "errors", 2, 1),
            ("Status", "detailed_status", 2, 2),
        ]
        
        for label_text, key, row, col in stats_config:
            frame = tk.Frame(stats_grid, bg=self.colors['bg_light'], 
                           relief=tk.RAISED, borderwidth=1)
            frame.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            
            tk.Label(frame, text=label_text, 
                    bg=self.colors['bg_light'],
                    fg=self.colors['accent'],
                    font=("Segoe UI", 8, "bold")).pack(pady=(3, 0))
            
            value_label = tk.Label(frame, text="0", 
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['text'],
                                  font=("Segoe UI", 14, "bold"))
            value_label.pack(pady=(0, 3))
            self.stat_labels[key] = value_label
        
        # Configure grid weights
        for i in range(3):
            stats_grid.columnconfigure(i, weight=1)
    
    def create_config_panel(self, parent):
        """Create configuration panel."""
        config_frame = tk.LabelFrame(parent, text="⚙️ Configuration", 
                                    bg=self.colors['bg_medium'],
                                    fg=self.colors['accent'],
                                    font=("Segoe UI", 11, "bold"),
                                    padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Create config grid
        configs = [
            ("Grid Size:", "GRID_SIZE", 1, 20),
            ("Harvest Count:", "HARVEST_COUNT", 1, 10),
            ("Move Delay (s):", "MOVE_DELAY", 0.05, 1.0),
            ("Harvest Delay (s):", "HARVEST_DELAY", 0.05, 1.0),
            ("Loop Cooldown (s):", "LOOP_COOLDOWN", 0, 10),
        ]
        
        self.config_vars = {}
        
        for i, (label_text, config_key, min_val, max_val) in enumerate(configs):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(config_frame, text=label_text, 
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text'],
                    font=("Segoe UI", 9)).grid(row=row, column=col, 
                                               padx=5, pady=5, sticky="w")
            
            var = tk.DoubleVar(value=getattr(Config, config_key))
            self.config_vars[config_key] = var
            
            spinbox = tk.Spinbox(config_frame, from_=min_val, to=max_val, 
                               textvariable=var, width=10,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text'],
                               buttonbackground=self.colors['accent'],
                               increment=0.05 if isinstance(min_val, float) else 1)
            spinbox.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
        
        save_btn = tk.Button(config_frame, text="💾 Save Config", 
                           command=self.save_config,
                           bg=self.colors['accent'], fg="black",
                           font=("Segoe UI", 9, "bold"),
                           cursor="hand2")
        save_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew", padx=5)
    
    def create_log_panel(self, parent):
        """Create log display panel."""
        log_frame = tk.LabelFrame(parent, text="📝 Activity Log", 
                                 bg=self.colors['bg_medium'],
                                 fg=self.colors['accent'],
                                 font=("Segoe UI", 11, "bold"),
                                 padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                  bg=self.colors['bg_light'],
                                                  fg=self.colors['text'],
                                                  font=("Consolas", 9),
                                                  wrap=tk.WORD,
                                                  state=tk.NORMAL)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored logs
        self.log_text.tag_config("info", foreground=self.colors['accent'])
        self.log_text.tag_config("success", foreground=self.colors['success'])
        self.log_text.tag_config("warning", foreground=self.colors['warning'])
        self.log_text.tag_config("error", foreground=self.colors['error'])
        
        self.log("Bot initialized. Ready to start!", "info")
    
    def log(self, message, tag="info"):
        """Add message to log with auto-scroll."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def create_footer(self):
        """Create footer."""
        footer = tk.Frame(self.root, bg=self.colors['bg_dark'], height=30)
        footer.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(footer, text="💡 Tip: Move mouse to top-left corner for emergency stop", 
                bg=self.colors['bg_dark'],
                fg=self.colors['text'],
                font=("Segoe UI", 8)).pack(side=tk.LEFT)
        
    def update_ui(self):
        """Update UI elements."""
        # Update stats
        self.stat_labels['cycles'].config(text=str(stats['cycles']))
        self.stat_labels['total_harvests'].config(text=str(stats['total_harvests']))
        self.stat_labels['total_sells'].config(text=str(stats['total_sells']))
        self.stat_labels['total_moves'].config(text=str(stats['total_moves']))
        self.stat_labels['errors'].config(text=str(stats['errors']))
        self.stat_labels['runtime'].config(text=get_elapsed_time())
        self.stat_labels['position'].config(
            text=f"({current_position['row']}, {current_position['col']})"
        )
        
        rate = get_harvests_per_hour()
        self.stat_labels['rate'].config(text=f"{rate:.1f}")
        
        # Update status
        if bot_running:
            self.stat_labels['detailed_status'].config(text="Running", 
                                                       fg=self.colors['success'])
            self.status_label.config(text="● RUNNING", fg=self.colors['success'])
        else:
            self.stat_labels['detailed_status'].config(text="Idle", 
                                                       fg=self.colors['warning'])
            self.status_label.config(text="● IDLE", fg=self.colors['warning'])
        
        # Schedule next update
        self.root.after(100, self.update_ui)
        
    def save_config(self):
        """Save configuration."""
        for key, var in self.config_vars.items():
            setattr(Config, key, int(var.get()) if key in ['GRID_SIZE', 'HARVEST_COUNT'] 
                   else float(var.get()))
        Config.save()
        self.log("Configuration saved!", "success")
        messagebox.showinfo("Success", "Configuration saved successfully!")
        
    def reset_stats(self):
        """Reset statistics."""
        if messagebox.askyesno("Reset Stats", "Are you sure you want to reset all statistics?"):
            stats['total_harvests'] = 0
            stats['total_sells'] = 0
            stats['total_moves'] = 0
            stats['errors'] = 0
            stats['inventory_checks'] = 0
            stats['cycles'] = 0
            stats['start_time'] = None
            self.log("Statistics reset!", "warning")
        
    def start_bot(self):
        """Start the bot."""
        global bot_running
        bot_running = True
        stats['start_time'] = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.log("Bot started! Switch to game window...", "success")
        
        # Start bot in separate thread
        bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        bot_thread.start()
        
    def stop_bot(self):
        """Stop the bot."""
        global bot_running
        bot_running = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log("Bot stopped by user.", "error")
        
    def run_bot(self):
        """Main bot loop."""
        time.sleep(3)
        self.log("Starting harvest loop...", "success")
        
        while bot_running:
            try:
                stats['cycles'] += 1
                self.log(f"━━━ Cycle #{stats['cycles']} started ━━━", "info")
                
                harvest_loop()
                
                if bot_running:
                    self.log(f"✓ Cycle #{stats['cycles']} complete!", "success")
                    if Config.LOOP_COOLDOWN > 0:
                        self.log(f"Waiting {Config.LOOP_COOLDOWN}s before next cycle...", "info")
                    time.sleep(Config.LOOP_COOLDOWN)
                    
            except Exception as e:
                self.log(f"ERROR: {e}", "error")
                stats['errors'] += 1
                time.sleep(2)

# =========================
# MAIN
# =========================

def main():
    global app
    root = tk.Tk()
    app = HarvestBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()