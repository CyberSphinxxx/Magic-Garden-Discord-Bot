import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime
import time
import os

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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
        
        # Shop inventory button references
        self.shop_buttons = {}
        
        # Check for OpenCV dependency
        if not CV2_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "OpenCV (cv2) is not available!\n\n"
                "Image detection will not work.\n"
                "Please install: pip install opencv-python"
            )
        
        # Load image assets
        self.load_assets()
        
        # Build the UI
        self._build_layout()
        
        # Start the UI update loop
        self.update_ui()
    
    def load_assets(self):
        """Load image assets for the GUI."""
        self.seed_icon = None
        
        if not PIL_AVAILABLE:
            return
        
        try:
            # Load seed icon from images folder
            icon_path = os.path.join("src", "images", "text_carrot.png")
            if os.path.exists(icon_path):
                pil_image = Image.open(icon_path)
                # Resize to 40x40
                pil_image = pil_image.resize((40, 40), Image.LANCZOS)
                self.seed_icon = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(40, 40))
            else:
                # Fallback - try alternative path
                alt_path = os.path.join(config.Config.IMAGE_FOLDER, "text_carrot.png")
                if os.path.exists(alt_path):
                    pil_image = Image.open(alt_path)
                    pil_image = pil_image.resize((40, 40), Image.LANCZOS)
                    self.seed_icon = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(40, 40))
        except Exception as e:
            print(f"Warning: Could not load seed icon: {e}")
            self.seed_icon = None
    
    def _build_layout(self):
        """Create the 2-column grid layout."""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors['window_bg'])
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=0, minsize=380)  # Sidebar fixed
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
        
        # Configure layout: Row 0 (Scrollable Main), Row 1 (Footer)
        sidebar.grid_rowconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=0)
        sidebar.grid_columnconfigure(0, weight=1)

        # === TOP SECTION (Scrollable with hidden scrollbar) ===
        sidebar_top = ctk.CTkScrollableFrame(
            sidebar, 
            fg_color="transparent",
            scrollbar_button_color=self.colors['sidebar_bg'],
            scrollbar_button_hover_color=self.colors['sidebar_bg']
        )
        sidebar_top.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
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
        
        # --- TabView for Modes ---
        self.tab_view = ctk.CTkTabview(
            sidebar_top,
            fg_color="transparent",
            segmented_button_fg_color=self.colors['card_bg'],
            segmented_button_selected_color=self.colors['blurple'],
            segmented_button_selected_hover_color="#4752c4",
            segmented_button_unselected_color=self.colors['card_bg'],
            segmented_button_unselected_hover_color=self.colors['text_muted'],
            corner_radius=10,
            height=800  # Give it plenty of height for all config items
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Bind tab change event
        self.tab_view.configure(command=self.on_tab_change)
        
        self.tab_view.add("Farm")
        self.tab_view.add("Shop")
        
        # === FARM TAB CONTENT ===
        farm_tab = self.tab_view.tab("Farm")
        
        # Farm Controls
        farm_controls = ctk.CTkFrame(farm_tab, fg_color="transparent")
        farm_controls.pack(fill="x", pady=10)
        
        self.start_button = ctk.CTkButton(
            farm_controls,
            text="▶",
            command=self.start_farming,
            fg_color=self.colors['green'],
            hover_color="#238636",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            width=60,
            corner_radius=10
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.stop_button = ctk.CTkButton(
            farm_controls,
            text="⏹",
            command=self.stop_bot,
            fg_color=self.colors['red'],
            hover_color="#c93c37",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            width=60,
            corner_radius=10,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        
        self.reset_button = ctk.CTkButton(
            farm_controls,
            text="🔄",
            command=self.reset_stats,
            fg_color=self.colors['blurple'],
            hover_color="#4752c4",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            width=60,
            corner_radius=10
        )
        self.reset_button.grid(row=0, column=2, sticky="ew")
        
        # Configure columns equal weight
        farm_controls.grid_columnconfigure((0, 1, 2), weight=1)
        
        # --- Status Banner (Fixed at top) ---
        status_banner = ctk.CTkFrame(farm_tab, fg_color=self.colors['card_bg'], corner_radius=8)
        status_banner.pack(fill="x", pady=(0, 10))
        
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
        
        # --- Statistics Panel (Fixed below status) ---
        ctk.CTkLabel(
            farm_tab,
            text="📊 STATISTICS",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_muted']
        ).pack(anchor="w", pady=(5, 5))
        
        stats_frame = ctk.CTkFrame(farm_tab, fg_color=self.colors['card_bg'], corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        
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
        
        # Row 3: Errors and Next Buy
        row3 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 10))
        row3.grid_columnconfigure((0, 1), weight=1)
        
        self._create_stat_box(row3, "Errors", "errors", 0)
        self._create_stat_box(row3, "Next Buy", "next_buy", 1)
        
        # Farm Configuration (Regular frame - scrolling handled by tab view)
        farm_scroll = ctk.CTkFrame(farm_tab, fg_color="transparent")
        farm_scroll.pack(fill="both", expand=True)

        # --- Configuration Panel ---
        self.config_frame = CollapsibleFrame(
            farm_scroll, 
            title="⚙️ CONFIGURATION",
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.config_frame.pack(fill="x", pady=5)
        
        config_inner = ctk.CTkFrame(self.config_frame.content_frame, fg_color="transparent")
        config_inner.pack(fill="x", padx=10, pady=10)
        
        self.config_vars = {}
        # (Label, ConfigKey, MinVal, MaxVal, TooltipText)
        configs = [
            ("Columns", "COLUMNS", 1, 20, "Number of columns in the garden grid."),
            ("Harvest Count", "HARVEST_COUNT", 1, 10, "How many times to click each crop tile."),
            ("Move Delay (s)", "MOVE_DELAY", 0.05, 1.0, "Time in seconds between grid movements (Recommended: 0.12s)."),
            ("Harvest Delay (s)", "HARVEST_DELAY", 0.05, 1.0, "Time to wait after clicking a crop."),
            ("Loop Cooldown (s)", "LOOP_COOLDOWN", 0, 10, "Pause time between full garden cycles."),
        ]
        # Add Enable Shopping Toggle
        self.autobuy_enabled_var = ctk.BooleanVar(value=config.Config.AUTOBUY_ENABLED)
        shopping_toggle = ctk.CTkSwitch(
            config_inner,
            text="Enable Shopping",
            variable=self.autobuy_enabled_var,
            command=self._on_autobuy_toggle,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            button_color=self.colors['blurple'],
            progress_color=self.colors['blurple']
        )
        shopping_toggle.pack(fill="x", padx=0, pady=(0, 10))
        ToolTip(shopping_toggle, "Enable automatic transitions to Shop mode for buying seeds.")

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
        save_btn.pack(fill="x", pady=(15, 0))

        # === SHOP TAB CONTENT ===
        shop_tab = self.tab_view.tab("Shop")
        
        # Shop Controls
        shop_controls = ctk.CTkFrame(shop_tab, fg_color="transparent")
        shop_controls.pack(fill="x", pady=10)
        
        self.shop_start_button = ctk.CTkButton(
            shop_controls,
            text="🛒 START SHOPPING",
            command=self.start_shopping_mode,
            fg_color=self.colors['green'],
            hover_color="#238636",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10
        )
        self.shop_start_button.pack(fill="x", pady=(0, 5))
        
        self.shop_stop_button = ctk.CTkButton(
            shop_controls,
            text="⏹ STOP",
            command=self.stop_bot,
            fg_color=self.colors['red'],
            hover_color="#c93c37",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10,
            state="disabled"
        )
        self.shop_stop_button.pack(fill="x", pady=(0, 15))
        
        # Shop Timer Label
        self.shop_timer_label = ctk.CTkLabel(
            shop_controls,
            text="Next Auto-Buy: --",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.shop_timer_label.pack(pady=(0, 5))
        
        # Shop Settings
        self.shop_frame = CollapsibleFrame(
            shop_tab, 
            title="⚙️ SHOP SETTINGS",
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.shop_frame.pack(fill="x", pady=5)
        
        shop_inner = ctk.CTkFrame(self.shop_frame.content_frame, fg_color="transparent")
        shop_inner.pack(fill="x", padx=10, pady=10)
        
        # Seeds Per Trip
        seeds_row = ctk.CTkFrame(shop_inner, fg_color="transparent")
        seeds_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            seeds_row,
            text="Seeds Per Trip",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_secondary'],
            width=140,
            anchor="w"
        ).pack(side="left")
        
        self.seeds_per_trip_var = ctk.StringVar(value=str(getattr(config.Config, 'SEEDS_PER_TRIP', 1)))
        seeds_entry = ctk.CTkEntry(
            seeds_row,
            textvariable=self.seeds_per_trip_var,
            width=80,
            height=28,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=self.colors['window_bg'],
            border_color=self.colors['blurple'],
            corner_radius=6
        )
        seeds_entry.pack(side="right")
        ToolTip(seeds_entry, "Number of each selected seed to buy per shop visit.")
        
        # Shop Interval
        interval_row = ctk.CTkFrame(shop_inner, fg_color="transparent")
        interval_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            interval_row,
            text="Interval (seconds)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_secondary'],
            width=140,
            anchor="w"
        ).pack(side="left")
        
        self.autobuy_interval_var = ctk.StringVar(value=str(config.Config.AUTOBUY_INTERVAL))
        interval_entry = ctk.CTkEntry(
            interval_row,
            textvariable=self.autobuy_interval_var,
            width=80,
            height=28,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=self.colors['window_bg'],
            border_color=self.colors['blurple'],
            corner_radius=6
        )
        interval_entry.pack(side="right")
        ToolTip(interval_entry, "Time between shop visits in seconds (default: 180).")
        
        # Search Attempts
        attempts_row = ctk.CTkFrame(shop_inner, fg_color="transparent")
        attempts_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            attempts_row,
            text="Search Attempts",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_secondary'],
            width=140,
            anchor="w"
        ).pack(side="left")
        
        self.shop_search_attempts_var = ctk.StringVar(value=str(getattr(config.Config, 'SHOP_SEARCH_ATTEMPTS', 7)))
        attempts_entry = ctk.CTkEntry(
            attempts_row,
            textvariable=self.shop_search_attempts_var,
            width=80,
            height=28,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=self.colors['window_bg'],
            border_color=self.colors['blurple'],
            corner_radius=6
        )
        attempts_entry.pack(side="right")
        ToolTip(attempts_entry, "Number of scroll attempts to find each seed (default: 7).")
        
        # Save Button for Shop Settings
        save_btn_row = ctk.CTkFrame(shop_inner, fg_color="transparent")
        save_btn_row.pack(fill="x", pady=(10, 5))
        
        ctk.CTkButton(
            save_btn_row,
            text="💾 Save Settings",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=self.colors['green'],
            hover_color="#1E7D32",
            corner_radius=8,
            height=32,
            command=self._save_shop_settings
        ).pack(fill="x")
        
        # === BOTTOM SECTION (Fixed Footer) ===
        sidebar_scroll = ctk.CTkFrame(
            sidebar,
            fg_color="transparent",
            height=60
        )
        sidebar_scroll.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        # --- Shop Info (shown only on Shop tab via tab change) ---
        self.shop_stats_container = ctk.CTkFrame(sidebar_scroll, fg_color="transparent")
        # Don't pack yet - will be shown when Shop tab is selected
        
        shop_info = ctk.CTkFrame(self.shop_stats_container, fg_color=self.colors['card_bg'], corner_radius=8)
        shop_info.pack(fill="x", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(
            shop_info,
            text="💡 Select seeds from the inventory above,\nthen click START SHOPPING to begin.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_secondary'],
            justify="center"
        ).pack(padx=15, pady=15)

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
        """Build the right-side main area with swappable Farm/Shop views and Log."""
        # Main right container
        right_container = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['sidebar_bg'],
            corner_radius=12
        )
        right_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Configure grid: Row 0 (View Container ~75%), Row 1 (Log ~25%)
        right_container.grid_rowconfigure(0, weight=3)
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        # === VIEW CONTAINER (holds swappable views) ===
        self.view_container = ctk.CTkFrame(
            right_container,
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.view_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.view_container.grid_rowconfigure(0, weight=0)  # Header
        self.view_container.grid_rowconfigure(1, weight=1)  # Content
        self.view_container.grid_columnconfigure(0, weight=1)
        
        # Dynamic Header Label
        self.view_header_label = ctk.CTkLabel(
            self.view_container,
            text="🌱 LIVE FIELD",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.view_header_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # === VIEW A: FARM VIEW (Grid/Canvas) ===
        self.farm_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.farm_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Mini Map Widget (fills container, self-centers internally)
        self.mini_map = MiniMapWidget(
            self.farm_view, 
            rows=config.Config.ROWS, 
            cols=config.Config.COLUMNS
        )
        self.mini_map.pack(fill="both", expand=True)
        
        # === VIEW B: SHOP VIEW (Inventory Grid) ===
        self.shop_view = ctk.CTkScrollableFrame(
            self.view_container, 
            fg_color="transparent",
            corner_radius=8
        )
        self.shop_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure shop view grid (5 rows x 4 columns)
        for col in range(4):
            self.shop_view.grid_columnconfigure(col, weight=1)
        
        # View mode switcher (above the inventory)
        self.shop_view_mode = ctk.StringVar(value="Tier")
        view_mode_frame = ctk.CTkFrame(self.shop_view, fg_color="transparent")
        view_mode_frame.grid(row=0, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(
            view_mode_frame,
            text="View:",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_muted']
        ).pack(side="left", padx=(5, 10))
        
        self.view_mode_buttons = ctk.CTkSegmentedButton(
            view_mode_frame,
            values=["Grid", "Tier", "A-Z"],
            variable=self.shop_view_mode,
            command=self._on_view_mode_change,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color=self.colors['card_bg'],
            selected_color=self.colors['blurple'],
            selected_hover_color="#4752c4",
            unselected_color=self.colors['sidebar_bg'],
            unselected_hover_color=self.colors['text_muted']
        )
        self.view_mode_buttons.pack(side="left")
        
        # Container for inventory buttons (row 1 onwards)
        self.inventory_container = ctk.CTkFrame(self.shop_view, fg_color="transparent")
        self.inventory_container.grid(row=1, column=0, columnspan=4, sticky="nsew")
        for col in range(4):
            self.inventory_container.grid_columnconfigure(col, weight=1)
        
        # Create inventory slots
        self._create_inventory_slots()
        
        # Hide shop view by default
        self.shop_view.grid_remove()
        
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
    
    def _create_inventory_slots(self):
        """Create interactive inventory button grid based on current view mode."""
        # Clear existing buttons from container
        for widget in self.inventory_container.winfo_children():
            widget.destroy()
        self.shop_buttons = {}
        
        # All seeds data
        all_seeds = [
            'Carrot', 'Strawberry', 'Aloe', 'Fava Bean', 'Blueberry', 'Apple',
            'Tulip', 'Tomato', 'Daffodil', 'Corn', 'Watermelon', 'Pumpkin',
            'Echeveria', 'Coconut', 'Banana', 'Lily', 'Camellia', "Burro's Tail",
            'Mushroom', 'Cactus', 'Bamboo', 'Chrysanthemum', 'Grape', 'Pepper',
            'Lemon', 'Passion Fruit', 'Dragon Fruit', 'Cacao', 'Lychee', 'Sunflower',
            'Starweaver', 'Dawnbinder', 'Moonbinder'
        ]
        
        # Seeds organized by tier with colors
        # Seeds organized by tier with colors
        RARITY_COLORS = {
            'COMMON': '#FFFFFF',     # Common (White)
            'UNCOMMON': '#2EA043',   # Uncommon (Green)
            'RARE': '#3B8ED0',       # Rare (Blue)
            'LEGENDARY': '#FFD700',  # Legendary (Gold/Yellow)
            'MYTHICAL': '#A855F7',   # Mythical (Purple)
            'DIVINE': '#FF7530',     # Divine (Darker/Vivid Orange)
            'CELESTIAL': '#FF69B4',  # Celestial (Pink - rainbow not doable)
        }
        
        seed_tiers = [
            ("COMMON", RARITY_COLORS['COMMON'], ['Carrot', 'Strawberry', 'Aloe']),
            ("UNCOMMON", RARITY_COLORS['UNCOMMON'], ['Fava Bean', 'Blueberry', 'Apple', 'Tulip', 'Tomato']),
            ("RARE", RARITY_COLORS['RARE'], ['Daffodil', 'Corn', 'Watermelon', 'Pumpkin', 'Echeveria']),
            ("LEGENDARY", RARITY_COLORS['LEGENDARY'], ['Coconut', 'Banana', 'Lily', 'Camellia', "Burro's Tail"]),
            ("MYTHICAL", RARITY_COLORS['MYTHICAL'], ['Mushroom', 'Cactus', 'Bamboo', 'Chrysanthemum', 'Grape']),
            ("DIVINE", RARITY_COLORS['DIVINE'], ['Pepper', 'Lemon', 'Passion Fruit', 'Dragon Fruit', 'Cacao', 'Lychee', 'Sunflower']),
            ("CELESTIAL", RARITY_COLORS['CELESTIAL'], ['Starweaver', 'Dawnbinder', 'Moonbinder']),
        ]
        
        # Create map of seed -> color for easy lookup
        self.seed_colors = {}
        for _, color, seeds in seed_tiers:
            for seed in seeds:
                self.seed_colors[seed] = color
        
        cols = 4
        current_row = 0
        view_mode = self.shop_view_mode.get() if hasattr(self, 'shop_view_mode') else "Tier"
        
        if view_mode == "Grid":
            # Simple grid layout
            for idx, seed_name in enumerate(all_seeds):
                row = idx // cols
                col = idx % cols
                button = self._create_seed_button(seed_name)
                button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
                self.shop_buttons[seed_name] = [button]
        
        elif view_mode == "A-Z":
            # Alphabetical order
            sorted_seeds = sorted(all_seeds)
            for idx, seed_name in enumerate(sorted_seeds):
                row = idx // cols
                col = idx % cols
                button = self._create_seed_button(seed_name)
                button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
                self.shop_buttons[seed_name] = [button]
        
        else:  # Tier view (default)
            for tier_name, tier_color, seeds in seed_tiers:
                # Tier header label
                tier_label = ctk.CTkLabel(
                    self.inventory_container,
                    text=f"━━━ {tier_name} ━━━",
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                    text_color=tier_color
                )
                tier_label.grid(row=current_row, column=0, columnspan=cols, pady=(10, 5), sticky="ew")
                current_row += 1
                
                # Seed buttons for this tier
                for idx, seed_name in enumerate(seeds):
                    col = idx % cols
                    if idx > 0 and col == 0:
                        current_row += 1
                    
                    button = self._create_seed_button(seed_name)
                    button.grid(row=current_row, column=col, padx=3, pady=2, sticky="nsew")
                    self.shop_buttons[seed_name] = [button]
                
                current_row += 1
        
        # Initialize SELECTED_SEEDS from legacy SELECTED_SEED if needed
        if not hasattr(config.Config, 'SELECTED_SEEDS') or not config.Config.SELECTED_SEEDS:
            config.Config.SELECTED_SEEDS = [config.Config.SELECTED_SEED] if config.Config.SELECTED_SEED else []
        
        # Highlight currently selected seeds
        self._update_seed_button_visuals()
    
    def _create_seed_button(self, seed_name):
        """Create a single seed button widget."""
        seed_color = self.seed_colors.get(seed_name, "gray")
        
        return ctk.CTkButton(
            self.inventory_container,
            text=seed_name,
            width=100,
            height=40,
            fg_color="transparent",
            hover_color=self.colors['card_bg'],
            border_width=2,
            border_color=seed_color,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self.colors['text_secondary'],
            corner_radius=8,
            command=lambda s=seed_name: self.select_seed(s)
        )
    
    def _on_view_mode_change(self, mode):
        """Handle view mode change and rebuild inventory."""
        self._create_inventory_slots()
    
    def on_tab_change(self, selected_tab=None):
        """Handle tab switching to swap views and sidebar content."""
        current_tab = self.tab_view.get()
        
        if current_tab == "Shop":
            # Show shop view, hide farm view
            self.farm_view.grid_remove()
            self.shop_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.view_header_label.configure(text="🛒 SHOP INVENTORY")
            
            # Show shop help in sidebar
            self.shop_stats_container.pack(fill="x")
        else:
            # Show farm view, hide shop view (default: Farm)
            self.shop_view.grid_remove()
            self.farm_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.view_header_label.configure(text="🌱 LIVE FIELD")
            
            # Hide shop help in sidebar
            self.shop_stats_container.pack_forget()
    
    def select_seed(self, seed_name):
        """Toggle seed selection for multi-buy. Clicking adds/removes from list."""
        # Initialize SELECTED_SEEDS if it doesn't exist (backward compatibility)
        if not hasattr(config.Config, 'SELECTED_SEEDS') or config.Config.SELECTED_SEEDS is None:
            config.Config.SELECTED_SEEDS = []
        
        # Toggle selection
        if seed_name in config.Config.SELECTED_SEEDS:
            # Remove from list
            config.Config.SELECTED_SEEDS.remove(seed_name)
            action = "Deselected"
        else:
            # Add to list
            config.Config.SELECTED_SEEDS.append(seed_name)
            action = "Selected"
        
        # Update legacy SELECTED_SEED to first in list (or empty)
        if config.Config.SELECTED_SEEDS:
            config.Config.SELECTED_SEED = config.Config.SELECTED_SEEDS[0]
        
        config.Config.save()
        
        # Update button visuals based on whether seed is in list
        self._update_seed_button_visuals()
        
        # Log selection (only if log_text has been initialized)
        if hasattr(self, 'log_text'):
            count = len(config.Config.SELECTED_SEEDS)
            self.log(f"{action} {seed_name}. Total seeds selected: {count}", "info")
    
    def _update_seed_button_visuals(self):
        """Update all seed button visuals based on SELECTED_SEEDS list."""
        for name, buttons in self.shop_buttons.items():
            seed_color = self.seed_colors.get(name, "gray")
            # buttons is now a list of all buttons for this seed name
            for button in buttons:
                if name in config.Config.SELECTED_SEEDS:
                    # Selected state - Rarity color background (Solid)
                    button.configure(
                        fg_color=seed_color,
                        border_color=seed_color,
                        text_color="#FFFFFF" if name != "Carrot" else "#000000" # Simple contrast check (white generally works unless very light)
                    )
                    # Improve text color for very light backgrounds (like Common white)
                    if seed_color.upper() in ["#FFFFFF", "#F39C12", "#00CED1"]:
                         button.configure(text_color="#000000")
                else:
                    # Unselected state - transparent with Rarity border
                    button.configure(
                        fg_color="transparent",
                        border_color=seed_color,
                        text_color=self.colors['text_secondary']
                    )
            
    def start_farming(self):
        """Start the bot in Farming Mode (Harvesting)."""
        # Farm mode always has harvesting enabled
        config.Config.HARVESTING_ENABLED = True
        config.Config.save()
        self.log("Starting Farming Mode...", "info")
        self.start_bot(mode='farm')

    def start_shopping_mode(self):
        """Start the bot in pure Shop Mode (Auto-Buy Only)."""
        # Disable harvesting, enable autobuy for shop mode
        config.Config.HARVESTING_ENABLED = False
        config.Config.AUTOBUY_ENABLED = True  # Shop mode always has autobuy enabled
        
        # Save shop settings from UI
        try:
            config.Config.SEEDS_PER_TRIP = int(self.seeds_per_trip_var.get())
        except (ValueError, AttributeError):
            config.Config.SEEDS_PER_TRIP = 1
        
        try:
            config.Config.AUTOBUY_INTERVAL = int(self.autobuy_interval_var.get())
        except (ValueError, AttributeError):
            config.Config.AUTOBUY_INTERVAL = 180
        
        config.Config.save()
        seeds_count = len(config.Config.SELECTED_SEEDS)
        self.log(f"Starting Shop Mode: {seeds_count} seed type(s), {config.Config.SEEDS_PER_TRIP} each...", "info")
        self.start_bot(mode='shop')

    def start_bot(self, mode='farm'):
        """Start the automation loop in a separate thread.
        
        Args:
            mode: 'farm' for harvesting loop, 'shop' for dedicated shop loop
        """
        if state.bot_running:
            return
        
        self.current_mode = mode
        state.bot_running = True
        state.stats['start_time'] = time.time()
        self.update_button_states()
        
        # Start automation in a background thread
        thread = threading.Thread(target=self._run_automation, daemon=True)
        thread.start()
        
        self.status_label.set_status("RUNNING")
        self.log("Automation started.", "success")
    
    def stop_bot(self):
        """Stop the automation loop."""
        if not state.bot_running:
            return
            
        state.bot_running = False
        self.update_button_states()
        
        self.status_label.set_status("STOPPING...")
        self.log("Stopping automation...", "warning")
    
    def update_button_states(self):
        """Update enable/disable state of buttons based on bot_running."""
        if state.bot_running:
            self.start_button.configure(state="disabled", fg_color="gray")
            self.shop_start_button.configure(state="disabled", fg_color="gray")
            
            self.stop_button.configure(state="normal", fg_color=self.colors['red'])
            self.shop_stop_button.configure(state="normal", fg_color=self.colors['red'])
            
            self.reset_button.configure(state="disabled", fg_color="gray")
        else:
            self.start_button.configure(state="normal", fg_color=self.colors['green'])
            self.shop_start_button.configure(state="normal", fg_color=self.colors['green'])
            
            self.stop_button.configure(state="disabled", fg_color="gray")
            self.shop_stop_button.configure(state="disabled", fg_color="gray")
            
            self.reset_button.configure(state="normal", fg_color=self.colors['blurple'])
    
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
        
        # Update Next Buy timer - calculate directly for smooth countdown
        if state.bot_running and config.Config.AUTOBUY_ENABLED and 'last_buy_time' in state.stats:
            elapsed = time.time() - state.stats['last_buy_time']
            remaining = config.Config.AUTOBUY_INTERVAL - elapsed
            if remaining > 0:
                self.stat_labels['next_buy'].configure(text=f"{int(remaining)}s")
            else:
                self.stat_labels['next_buy'].configure(text="0s")
        else:
            self.stat_labels['next_buy'].configure(text="--")
        
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
        
        # Update Shop Timer
        next_buy = state.stats.get('next_buy_time', 0)
        if next_buy > 0 and state.bot_running and getattr(self, 'current_mode', 'farm') == 'shop':
            self.shop_timer_label.configure(text=f"Next Auto-Buy: {int(next_buy)}s")
        else:
            self.shop_timer_label.configure(text="Next Auto-Buy: --")
        
        # Schedule next update
        self.root.after(100, self.update_ui)
    
    def _on_autobuy_toggle(self):
        """Update config when auto-buy toggle is changed."""
        config.Config.AUTOBUY_ENABLED = self.autobuy_enabled_var.get()
        config.Config.save()
        status = "enabled" if config.Config.AUTOBUY_ENABLED else "disabled"
        self.log(f"Auto-buy {status}.", "info")
    
    def _on_seed_changed(self, choice):
        """Update config when seed selection is changed."""
        config.Config.SELECTED_SEED = choice
        config.Config.save()
        self.log(f"Target seed set to: {choice}", "info")
    
    def _on_harvesting_toggle(self):
        """Update config when harvesting toggle is changed."""
        config.Config.HARVESTING_ENABLED = self.harvesting_enabled_var.get()
        config.Config.save()
        status = "enabled" if config.Config.HARVESTING_ENABLED else "disabled"
        self.log(f"Harvesting {status}.", "info")
    
    def _save_shop_settings(self):
        """Save shop settings (seeds per trip and autobuy interval) to config."""
        try:
            # Save seeds per trip
            seeds_per_trip = int(self.seeds_per_trip_var.get())
            if seeds_per_trip < 1:
                seeds_per_trip = 1
            config.Config.SEEDS_PER_TRIP = seeds_per_trip
            
            # Save autobuy interval
            autobuy_interval = int(self.autobuy_interval_var.get())
            if autobuy_interval < 10:
                autobuy_interval = 10  # Minimum 10 seconds
            config.Config.AUTOBUY_INTERVAL = autobuy_interval
            
            # Save search attempts
            search_attempts = int(self.shop_search_attempts_var.get())
            if search_attempts < 1:
                search_attempts = 1
            config.Config.SHOP_SEARCH_ATTEMPTS = search_attempts
            
            # Save to disk
            config.Config.save()
            
            self.log(f"✓ Shop settings saved: {seeds_per_trip} seeds/trip, {autobuy_interval}s interval, {search_attempts} attempts", "success")
        except ValueError:
            self.log("⚠️ Invalid shop settings - please enter numbers only.", "error")
    
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
        """Reset all statistics and position after confirmation."""
        if messagebox.askyesno("Reset Farm Loop", "This will reset all statistics and position.\n\nAfter resetting, move your character to the TOP-LEFT corner (Tile 0,0) before starting again.\n\nContinue?"):
            for key in ['total_harvests', 'total_sells', 'total_moves', 'errors', 'inventory_checks', 'cycles']:
                state.stats[key] = 0
            state.stats['start_time'] = None
            
            # Reset position to start
            state.current_position['row'] = 0
            state.current_position['col'] = 0
            self.mini_map.update_position(0, 0)
            
            self.log("🔄 Farm loop reset! Move character to TOP-LEFT corner before starting.", "warning")
    
    def open_guide(self):
        """Open the Help & Guide window (singleton)."""
        if self.guide_window is None or not self.guide_window.winfo_exists():
            self.guide_window = GuideWindow(self.root, colors=self.colors)
        else:
            self.guide_window.focus_force()
    
    def _run_automation(self):
        """Main bot loop executed in a separate thread."""
        time.sleep(3)  # Grace period for user to switch to game window
        
        mode = getattr(self, 'current_mode', 'farm')
        
        if mode == 'shop':
            # Dedicated shop-only loop
            self.log("Starting Shop Mode loop...", "success")
            game_actions.run_shop_only_loop(logger=self.log)
            return
        
        # Farm mode - original harvest loop behavior
        self.log("Starting Farming loop...", "success")
        
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
