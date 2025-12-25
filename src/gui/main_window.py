import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime
import time

from src.core import state, config, game_actions
from src.core.automation import CV2_AVAILABLE
from src.gui.mini_map import MiniMapWidget
from src.gui.status_badge import StatusBadge
from src.gui.collapsible_frame import CollapsibleFrame
from src.gui.tooltip import ToolTip
from src.gui.guide_window import GuideWindow


class HarvestBotGUI:
    """Modern Gaming Dashboard for Magic Garden Bot using customtkinter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 Magic Garden Bot")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        
        # Discord-inspired color palette
        self.colors = {
            'window_bg': "#2b2d31",
            'sidebar_bg': "#313338",
            'card_bg': "#2f3136",
            'blurple': "#5865F2",
            'green': "#2EA043",
            'red': "#ED4245",
            'text_primary': "#FFFFFF",
            'text_secondary': "#B5BAC1",
            'text_muted': "#949BA4",
        }
        
        # Configure customtkinter appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Set window background
        self.root.configure(fg_color=self.colors['window_bg'])
        
        # Auto-scroll state
        self.auto_scroll = ctk.BooleanVar(value=True)
        
        # Guide window reference (singleton)
        self.guide_window = None
        
        # Check for OpenCV dependency
        if not CV2_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "OpenCV (cv2) is not available!\n\n"
                "Image detection will not work.\n"
                "Please install: pip install opencv-python"
            )
        
        # Build the UI
        self._build_layout()
        
        # Start the UI update loop
        self.update_ui()
    
    def _build_layout(self):
        """Create the 2-column grid layout."""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors['window_bg'])
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=0, minsize=300)  # Sidebar fixed
        self.main_container.grid_columnconfigure(1, weight=1)  # Log expands
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left Sidebar
        self._build_sidebar()
        
        # Right Main Area (Map + Log)
        self._build_main_area()
    
    def _build_sidebar(self):
        """Build the left sidebar with fixed Top and scrollable Bottom sections."""
        sidebar = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.colors['sidebar_bg'],
            corner_radius=12
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Configure layout: Row 0 (Fixed), Row 1 (Scrollable)
        sidebar.grid_rowconfigure(0, weight=0)
        sidebar.grid_rowconfigure(1, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        # === TOP SECTION (Fixed) ===
        sidebar_top = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_top.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # --- Header ---
        header_frame = ctk.CTkFrame(sidebar_top, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title row with Help button
        title_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_row.pack(fill="x")
        
        ctk.CTkLabel(
            title_row,
            text="🌱 Magic Garden Bot",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        # Help button (subtle)
        help_btn = ctk.CTkButton(
            title_row,
            text="?",
            command=self.open_guide,
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#4a4a4a",
            text_color=self.colors['text_muted'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            corner_radius=14
        )
        help_btn.pack(side="right")
        
        ctk.CTkLabel(
            header_frame,
            text="Automation Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors['text_muted']
        ).pack(anchor="w")
        
        # --- Control Buttons ---
        control_frame = ctk.CTkFrame(sidebar_top, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=15)
        
        # Button container for horizontal layout
        btn_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_container.pack(fill="x")
        btn_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_button = ctk.CTkButton(
            btn_container,
            text="▶ START",
            command=self.start_bot,
            fg_color=self.colors['green'],
            hover_color="#238636",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10
        )
        self.start_button.grid(row=0, column=0, padx=2, sticky="ew")
        
        self.stop_button = ctk.CTkButton(
            btn_container,
            text="⏹ STOP",
            command=self.stop_bot,
            fg_color=self.colors['red'],
            hover_color="#c93c37",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.reset_button = ctk.CTkButton(
            btn_container,
            text="🔄 RESET",
            command=self.reset_stats,
            fg_color=self.colors['blurple'],
            hover_color="#4752c4",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10
        )
        self.reset_button.grid(row=0, column=2, padx=2, sticky="ew")

        # === BOTTOM SECTION (Scrollable) ===
        sidebar_scroll = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            label_text="",
            height=200
        )
        sidebar_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # --- Status Banner (Horizontal, Compact) ---
        status_banner = ctk.CTkFrame(sidebar_scroll, fg_color=self.colors['card_bg'], corner_radius=8)
        status_banner.pack(fill="x", padx=20, pady=(10, 5))
        
        # Horizontal layout
        status_row = ctk.CTkFrame(status_banner, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            status_row,
            text="STATUS:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.colors['text_muted']
        ).pack(side="left")
        
        self.status_label = StatusBadge(status_row)
        self.status_label.pack(side="right")
        
        # --- Statistics Panel ---
        stats_label = ctk.CTkLabel(
            sidebar_scroll,
            text="📊 STATISTICS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.colors['text_muted']
        )
        stats_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        stats_frame = ctk.CTkFrame(sidebar_scroll, fg_color=self.colors['card_bg'], corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        self.stat_labels = {}
        
        # Row 1: Cycles, Runtime, Cycle Speed
        row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)
        row1.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._create_stat_box(row1, "Cycles", "cycles", 0)
        self._create_stat_box(row1, "Runtime", "runtime", 1)
        self._create_stat_box(row1, "Cycle Speed", "cycle_speed", 2)
        
        # Row 2: Harvests, Sells, Moves
        row2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))
        row2.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._create_stat_box(row2, "Harvests", "total_harvests", 0)
        self._create_stat_box(row2, "Sells", "total_sells", 1)
        self._create_stat_box(row2, "Moves", "total_moves", 2)
        
        # Row 3: Errors
        row3 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 10))
        row3.grid_columnconfigure(0, weight=1)
        
        self._create_stat_box(row3, "Errors", "errors", 0)
        
        
        # --- Configuration Panel (Collapsible) ---
        self.config_frame = CollapsibleFrame(
            sidebar_scroll, 
            title="⚙️ CONFIGURATION",
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.config_frame.pack(fill="x", padx=20, pady=5)
        
        config_inner = ctk.CTkFrame(self.config_frame.content_frame, fg_color="transparent")
        config_inner.pack(fill="x", padx=15, pady=15)
        
        self.config_vars = {}
        # (Label, ConfigKey, MinVal, MaxVal, TooltipText)
        configs = [
            ("Columns", "COLUMNS", 1, 20, "Number of columns in the garden grid."),
            ("Harvest Count", "HARVEST_COUNT", 1, 10, "How many times to click each crop tile."),
            ("Move Delay (s)", "MOVE_DELAY", 0.05, 1.0, "Time in seconds between grid movements (Recommended: 0.12s)."),
            ("Harvest Delay (s)", "HARVEST_DELAY", 0.05, 1.0, "Time to wait after clicking a crop."),
            ("Loop Cooldown (s)", "LOOP_COOLDOWN", 0, 10, "Pause time between full garden cycles."),
        ]
        
        for i, (label_text, config_key, min_val, max_val, tooltip_text) in enumerate(configs):
            row_frame = ctk.CTkFrame(config_inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                row_frame,
                text=label_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=self.colors['text_secondary'],
                width=120,
                anchor="w"
            ).pack(side="left")
            
            var = ctk.StringVar(value=str(getattr(config.Config, config_key)))
            self.config_vars[config_key] = var
            
            entry = ctk.CTkEntry(
                row_frame,
                textvariable=var,
                width=80,
                height=28,
                font=ctk.CTkFont(family="Consolas", size=11),
                fg_color=self.colors['window_bg'],
                border_color=self.colors['blurple'],
                corner_radius=6
            )
            entry.pack(side="right")
            
            # Attach tooltip to entry
            ToolTip(entry, tooltip_text)
        
        # Save Config Button
        save_btn = ctk.CTkButton(
            config_inner,
            text="💾 Save Configuration",
            command=self.save_config,
            fg_color=self.colors['blurple'],
            hover_color="#4752c4",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            corner_radius=8
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, 5), pady=(15, 0))
        
        # Reset Defaults Button
        reset_defaults_btn = ctk.CTkButton(
            config_inner,
            text="↺ Reset",
            command=self.reset_configuration,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            corner_radius=8
        )
        reset_defaults_btn.pack(side="right", expand=True, fill="x", padx=(5, 0), pady=(15, 0))
        
        # --- Footer ---
        footer = ctk.CTkLabel(
            sidebar_scroll,
            text="Created by John Lemar Gonzales",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=self.colors['text_muted']
        )
        footer.pack(side="bottom", pady=10)
    
    def _create_stat_box(self, parent, label, key, col):
        """Create a single stat display box with value as hero element."""
        box = ctk.CTkFrame(parent, fg_color=self.colors['sidebar_bg'], corner_radius=8)
        box.grid(row=0, column=col, padx=3, pady=2, sticky="ew")
        
        # Value (Hero) - Large, bold, bright white, centered
        value_label = ctk.CTkLabel(
            box,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.colors['text_primary']
        )
        value_label.pack(pady=(12, 0))
        self.stat_labels[key] = value_label
        
        # Label (Secondary) - Small, muted grey, below the value
        ctk.CTkLabel(
            box,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="gray70"
        ).pack(pady=(2, 10))
    
    def _build_main_area(self):
        """Build the right-side main area with Map and Log."""
        # Main right container
        right_container = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['sidebar_bg'],
            corner_radius=12
        )
        right_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Configure grid: Row 0 (Map ~75%), Row 1 (Log ~25%)
        right_container.grid_rowconfigure(0, weight=3)
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        # === LIVE FIELD (Map) ===
        live_field_frame = ctk.CTkFrame(
            right_container,
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        live_field_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        # Header for Live Field
        ctk.CTkLabel(
            live_field_frame,
            text="🌱 LIVE FIELD",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Map Container (centered)
        map_container = ctk.CTkFrame(live_field_frame, fg_color="transparent")
        map_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mini Map Widget (fills container, self-centers internally)
        self.mini_map = MiniMapWidget(
            map_container, 
            rows=config.Config.ROWS, 
            cols=config.Config.COLUMNS
        )
        self.mini_map.pack(fill="both", expand=True)
        
        # === ACTIVITY LOG ===
        log_container = ctk.CTkFrame(
            right_container,
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Header for Log
        ctk.CTkLabel(
            log_container,
            text="📝 Activity Log",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", padx=15, pady=(8, 5))
        
        # Log textbox (font size 11 as requested)
        self.log_text = ctk.CTkTextbox(
            log_container,
            fg_color=self.colors['window_bg'],
            text_color=self.colors['text_secondary'],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            wrap="word",
            state="normal"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Configure text tags for colored messages
        self.log_text.tag_config("info", foreground=self.colors['blurple'])
        self.log_text.tag_config("success", foreground=self.colors['green'])
        self.log_text.tag_config("warning", foreground="#FAA61A")
        self.log_text.tag_config("error", foreground=self.colors['red'])
        
        # Initial log messages
        self.log("Bot initialized. Ready to start!", "info")
        if CV2_AVAILABLE:
            self.log("✓ OpenCV loaded successfully", "success")
        else:
            self.log("✗ OpenCV NOT available - image detection disabled!", "error")
    
    def log(self, message, tag="info"):
        """Add a timestamped message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n", tag)
        self.log_text.configure(state="disabled")
        
        if self.auto_scroll.get():
            self.log_text.see("end")
        
        self.root.update_idletasks()
    
    def get_elapsed_time(self):
        """Calculate and format elapsed runtime."""
        if state.stats['start_time']:
            elapsed = time.time() - state.stats['start_time']
            h, r = divmod(elapsed, 3600)
            m, s = divmod(r, 60)
            return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
        return "00:00:00"
    
    def get_avg_cycle_time(self):
        """Calculate average cycle time from the last 10 entries."""
        times = state.stats.get('cycle_times', [])
        if times:
            return sum(times) / len(times)
        return 0.0
    
    def update_ui(self):
        """Periodically update all dynamic UI elements."""
        s = state.stats
        
        # Update stat labels
        self.stat_labels['cycles'].configure(text=str(s['cycles']))
        self.stat_labels['total_harvests'].configure(text=str(s['total_harvests']))
        self.stat_labels['total_sells'].configure(text=str(s['total_sells']))
        self.stat_labels['total_moves'].configure(text=str(s['total_moves']))
        self.stat_labels['errors'].configure(text=str(s['errors']))
        self.stat_labels['runtime'].configure(text=self.get_elapsed_time())
        self.mini_map.update_position(state.current_position['row'], state.current_position['col'])
        
        # Format Cycle Speed: "14.2s"
        avg_time = self.get_avg_cycle_time()
        self.stat_labels['cycle_speed'].configure(text=f"{avg_time:.1f}s")
        
        # Update status indicator
        if state.bot_running:
            self.status_label.set_status("RUNNING")
        else:
            # Check if it was explicitly stopped or just idle?
            # For now, default to IDLE if not running. 
            # If we want "STOPPED", we need to track that state more explicitly or rely on last action.
            # But the requirement said: STOPPED: Background Red.
            # I'll stick to IDLE logic unless I add a specific 'stopped' state flag.
            # Let's check the text of the badge to decide? No, that's messy.
            # Let's just use IDLE for !running as per original behavior, unless I modify stop_bot.
            if self.status_label.current_status != "STOPPED":
                 self.status_label.set_status("IDLE")
        
        # Schedule next update
        self.root.after(100, self.update_ui)
    
    def save_config(self):
        """Save current configuration values."""
        try:
            for key, var in self.config_vars.items():
                str_value = var.get().strip()
                if str_value == "":
                    self.log(f"Config error: {key} is empty.", "error")
                    return
                value = float(str_value)
                # Convert to int if it's a whole number
                setattr(config.Config, key, int(value) if value.is_integer() else value)
            config.Config.save()
            self.log("Configuration saved!", "success")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except ValueError as e:
            self.log(f"Config error: Invalid number format.", "error")
            messagebox.showerror("Error", f"Invalid configuration value. Please enter numbers only.")
    
    def reset_configuration(self):
        """Reset all configuration values to safe defaults."""
        defaults = {
            'COLUMNS': '10',
            'HARVEST_COUNT': '5',
            'MOVE_DELAY': '0.12',
            'HARVEST_DELAY': '0.1',
            'LOOP_COOLDOWN': '2',
        }
        for key, default_value in defaults.items():
            if key in self.config_vars:
                self.config_vars[key].set(default_value)
        self.log("Configuration reset to defaults.", "warning")
    
    def reset_stats(self):
        """Reset all statistics after confirmation."""
        if messagebox.askyesno("Reset Stats", "Are you sure you want to reset all statistics?"):
            for key in ['total_harvests', 'total_sells', 'total_moves', 'errors', 'inventory_checks', 'cycles']:
                state.stats[key] = 0
            state.stats['start_time'] = None
            self.log("Statistics reset!", "warning")
    
    def open_guide(self):
        """Open the Help & Guide window (singleton)."""
        if self.guide_window is None or not self.guide_window.winfo_exists():
            self.guide_window = GuideWindow(self.root, colors=self.colors)
        else:
            self.guide_window.focus_force()
    
    def start_bot(self):
        """Start the automation bot with a 3-second countdown."""
        if not CV2_AVAILABLE:
            messagebox.showerror("Cannot Start", "OpenCV is not available. Please install: pip install opencv-python")
            return
        
        # Disable buttons during countdown
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        
        # Initial log message
        self.log("⚠️ Switch to Game Window NOW!", "warning")
        
        # Start countdown
        self._countdown_tick(3)
    
    def _countdown_tick(self, count):
        """Handle countdown tick."""
        if count > 0:
            # Update button appearance
            self.start_button.configure(
                text=f"Starting in {count}...",
                fg_color="#F59E0B",  # Amber/Orange
                hover_color="#D97706"
            )
            self.log(f"Starting in {count}...", "warning")
            # Schedule next tick
            self.root.after(1000, lambda: self._countdown_tick(count - 1))
        else:
            # Countdown complete - start the bot
            self._launch_bot()
    
    def _launch_bot(self):
        """Actually start the bot after countdown."""
        state.bot_running = True
        state.stats['start_time'] = time.time()
        
        # Update button to STOP state
        self.start_button.configure(
            text="▶ START",
            fg_color=self.colors['green'],
            hover_color="#238636",
            state="disabled"
        )
        self.stop_button.configure(state="normal")
        
        self.log("Bot started! Switch to game window NOW!", "success")
        
        bot_thread = threading.Thread(target=self.run_bot_thread, daemon=True)
        bot_thread.start()
    
    def stop_bot(self):
        """Stop the automation bot."""
        state.bot_running = False
        self.start_button.configure(
            text="▶ START",
            fg_color=self.colors['green'],
            hover_color="#238636",
            state="normal"
        )
        self.stop_button.configure(state="disabled")
        self.status_label.set_status("STOPPED")
        self.log("Bot stopped by user.", "error")
    
    def run_bot_thread(self):
        """Main bot loop executed in a separate thread."""
        time.sleep(3)  # Grace period for user to switch to game window
        self.log("Starting harvest loop...", "success")
        
        while state.bot_running:
            try:
                state.stats['cycles'] += 1
                if state.bot_running:
                    # Calculate cycle duration
                    cycle_start = time.time()
                    self.log(f"━━━ Cycle #{state.stats['cycles']} started ━━━", "info")
                    
                    game_actions.harvest_loop(logger=self.log)
                    
                    # Record duration
                    duration = time.time() - cycle_start
                    state.stats['cycle_times'].append(duration)
                    # Keep only the last 10
                    state.stats['cycle_times'] = state.stats['cycle_times'][-10:]
                    
                    self.log(f"✓ Cycle #{state.stats['cycles']} complete! ({duration:.1f}s)", "success")
                    if config.Config.LOOP_COOLDOWN > 0:
                        self.log(f"Waiting {config.Config.LOOP_COOLDOWN}s before next cycle...", "info")
                    time.sleep(config.Config.LOOP_COOLDOWN)
                    
            except Exception as e:
                self.log(f"An unexpected error occurred in bot thread: {e}", "error")
                state.stats['errors'] += 1
                time.sleep(2)
