"""
Magic Garden Bot - Main Window GUI.

Modern Gaming Dashboard for Magic Garden Bot using customtkinter.
This module has been refactored for better maintainability and scalability.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import time
import os

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from src.core import state, config
from src.core.automation import CV2_AVAILABLE
from src.gui.mini_map import MiniMapWidget
from src.gui.status_badge import StatusBadge
from src.gui.collapsible_frame import CollapsibleFrame
from src.gui.guide_window import GuideWindow

# Import refactored modules
from src.gui.constants import (
    UI_COLORS, VIEW_MODES, INVENTORY_COLUMNS, 
    FONT_FAMILY, get_seed_color_map
)
from src.gui.ui_builders import (
    InventoryBuilder, StatisticsPanelBuilder, 
    ConfigurationPanelBuilder, ShopSettingsBuilder,
    create_control_button
)
from src.gui.controllers import BotController, ConfigController, SeedController

# Import update functionality
from src.core.updater import (
    CURRENT_VERSION, check_for_updates_async, 
    download_update_async, apply_update
)
from src.gui.update_dialog import UpdateDialog, NoUpdateDialog


class HarvestBotGUI:
    """Modern Gaming Dashboard for Magic Garden Bot using customtkinter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 Magic Garden Bot")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        
        # Use centralized color palette
        self.colors = UI_COLORS
        
        # Configure customtkinter appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Set window background
        self.root.configure(fg_color=self.colors['window_bg'])
        
        # Auto-scroll state
        self.auto_scroll = ctk.BooleanVar(value=True)
        
        # Guide window reference (singleton)
        self.guide_window = None
        
        # Initialize builders
        self.inventory_builder = InventoryBuilder(self.colors)
        
        # Initialize controllers
        self.bot_controller = BotController(self)
        self.config_controller = ConfigController(self)
        self.seed_controller = SeedController(self, self.inventory_builder)
        
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
                pil_image = pil_image.resize((40, 40), Image.LANCZOS)
                self.seed_icon = ctk.CTkImage(
                    light_image=pil_image, 
                    dark_image=pil_image, 
                    size=(40, 40)
                )
            else:
                # Fallback - try alternative path
                alt_path = os.path.join(config.Config.IMAGE_FOLDER, "text_carrot.png")
                if os.path.exists(alt_path):
                    pil_image = Image.open(alt_path)
                    pil_image = pil_image.resize((40, 40), Image.LANCZOS)
                    self.seed_icon = ctk.CTkImage(
                        light_image=pil_image, 
                        dark_image=pil_image, 
                        size=(40, 40)
                    )
        except Exception as e:
            print(f"Warning: Could not load seed icon: {e}")
            self.seed_icon = None
    
    def _build_layout(self):
        """Create the 2-column grid layout."""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors['window_bg'])
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=0, minsize=380)
        self.main_container.grid_columnconfigure(1, weight=1)
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
        self._build_header(sidebar_top)
        
        # --- TabView for Modes ---
        self._build_tab_view(sidebar_top)
        
        # === BOTTOM SECTION (Fixed Footer) ===
        self._build_footer(sidebar)
    
    def _build_header(self, parent):
        """Build the header section with title and help button."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title row with Help button
        title_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_row.pack(fill="x")
        
        ctk.CTkLabel(
            title_row,
            text="🌱 Magic Garden Bot",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
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
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            corner_radius=14
        )
        help_btn.pack(side="right")
        
        ctk.CTkLabel(
            header_frame,
            text="Automation Dashboard",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=self.colors['text_muted']
        ).pack(anchor="w")
    
    def _build_tab_view(self, parent):
        """Build the tabbed interface for Farm and Shop modes."""
        self.tab_view = ctk.CTkTabview(
            parent,
            fg_color="transparent",
            segmented_button_fg_color=self.colors['card_bg'],
            segmented_button_selected_color=self.colors['blurple'],
            segmented_button_selected_hover_color="#4752c4",
            segmented_button_unselected_color=self.colors['card_bg'],
            segmented_button_unselected_hover_color=self.colors['text_muted'],
            corner_radius=10,
            height=800
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Bind tab change event
        self.tab_view.configure(command=self.on_tab_change)
        
        self.tab_view.add("Farm")
        self.tab_view.add("Shop")
        
        # Build tab contents
        self._build_farm_tab()
        self._build_shop_tab()
    
    def _build_farm_tab(self):
        """Build the Farm tab content."""
        farm_tab = self.tab_view.tab("Farm")
        
        # Farm Controls
        farm_controls = ctk.CTkFrame(farm_tab, fg_color="transparent")
        farm_controls.pack(fill="x", pady=10)
        
        self.start_button = create_control_button(
            farm_controls, "▶", self.start_farming,
            self.colors['green'], "#238636"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.stop_button = create_control_button(
            farm_controls, "⏹", self.stop_bot,
            self.colors['red'], "#c93c37", state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        
        self.reset_button = create_control_button(
            farm_controls, "🔄", self.reset_stats,
            self.colors['blurple'], "#4752c4"
        )
        self.reset_button.grid(row=0, column=2, sticky="ew")
        
        farm_controls.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Status Banner
        self._build_status_banner(farm_tab)
        
        # Statistics Panel (using builder)
        stats_builder = StatisticsPanelBuilder(self.colors)
        self.stat_labels = stats_builder.build(farm_tab)
        
        # Farm Configuration
        farm_scroll = ctk.CTkFrame(farm_tab, fg_color="transparent")
        farm_scroll.pack(fill="both", expand=True)
        
        self.config_frame = CollapsibleFrame(
            farm_scroll, 
            title="⚙️ CONFIGURATION",
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.config_frame.pack(fill="x", pady=5)
        
        # Build configuration panel (using builder)
        self.autobuy_enabled_var = ctk.BooleanVar(value=config.Config.AUTOBUY_ENABLED)
        config_builder = ConfigurationPanelBuilder(self.colors)
        self.config_vars = config_builder.build(
            self.config_frame.content_frame,
            self.autobuy_enabled_var,
            self._on_autobuy_toggle,
            self.save_config
        )
    
    def _build_status_banner(self, parent):
        """Build the status banner section."""
        status_banner = ctk.CTkFrame(parent, fg_color=self.colors['card_bg'], corner_radius=8)
        status_banner.pack(fill="x", pady=(0, 10))
        
        status_row = ctk.CTkFrame(status_banner, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(
            status_row,
            text="STATUS:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=self.colors['text_muted']
        ).pack(side="left")
        
        self.status_label = StatusBadge(status_row)
        self.status_label.pack(side="right")
    
    def _build_shop_tab(self):
        """Build the Shop tab content."""
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
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
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
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            height=40,
            corner_radius=10,
            state="disabled"
        )
        self.shop_stop_button.pack(fill="x", pady=(0, 15))
        
        # Shop Timer Label
        self.shop_timer_label = ctk.CTkLabel(
            shop_controls,
            text="Next Auto-Buy: --",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        self.shop_timer_label.pack(pady=(0, 5))
        
        # Shop Settings (using builder)
        self.shop_frame = CollapsibleFrame(
            shop_tab, 
            title="⚙️ SHOP SETTINGS",
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.shop_frame.pack(fill="x", pady=5)
        
        shop_settings_builder = ShopSettingsBuilder(self.colors)
        (self.seeds_per_trip_var, 
         self.autobuy_interval_var, 
         self.shop_search_attempts_var) = shop_settings_builder.build(
            self.shop_frame.content_frame,
            self._save_shop_settings
        )
    
    def _build_footer(self, sidebar):
        """Build the sidebar footer section."""
        sidebar_scroll = ctk.CTkFrame(sidebar, fg_color="transparent", height=60)
        sidebar_scroll.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        # Shop Info (shown only on Shop tab via tab change)
        self.shop_stats_container = ctk.CTkFrame(sidebar_scroll, fg_color="transparent")
        
        shop_info = ctk.CTkFrame(
            self.shop_stats_container, 
            fg_color=self.colors['card_bg'], 
            corner_radius=8
        )
        shop_info.pack(fill="x", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(
            shop_info,
            text="💡 Select seeds from the inventory above,\nthen click START SHOPPING to begin.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            justify="center"
        ).pack(padx=15, pady=15)

        # Footer
        footer = ctk.CTkLabel(
            sidebar_scroll,
            text="Created by John Lemar Gonzales",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=self.colors['text_muted']
        )
        footer.pack(side="bottom", pady=10)
        
        # Version button (clickable for update check)
        self.version_button = ctk.CTkButton(
            sidebar_scroll,
            text=f"🔄 v{CURRENT_VERSION}",
            command=self.check_for_updates,
            fg_color="transparent",
            hover_color=self.colors['card_bg'],
            text_color=self.colors['text_muted'],
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            height=24,
            cursor="hand2"
        )
        self.version_button.pack(side="bottom", pady=(0, 5))
    
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
        
        # View Container
        self._build_view_container(right_container)
        
        # Activity Log
        self._build_activity_log(right_container)
    
    def _build_view_container(self, parent):
        """Build the swappable view container for Farm/Shop views."""
        self.view_container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        self.view_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.view_container.grid_rowconfigure(0, weight=0)
        self.view_container.grid_rowconfigure(1, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)
        
        # Dynamic Header Label
        self.view_header_label = ctk.CTkLabel(
            self.view_container,
            text="🌱 LIVE FIELD",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.view_header_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # Farm View
        self._build_farm_view()
        
        # Shop View
        self._build_shop_view()
    
    def _build_farm_view(self):
        """Build the farm view with mini map."""
        self.farm_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.farm_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Mini Map Widget
        self.mini_map = MiniMapWidget(
            self.farm_view, 
            rows=config.Config.ROWS, 
            cols=config.Config.COLUMNS
        )
        self.mini_map.pack(fill="both", expand=True)
    
    def _build_shop_view(self):
        """Build the shop view with inventory grid."""
        self.shop_view = ctk.CTkScrollableFrame(
            self.view_container, 
            fg_color="transparent",
            corner_radius=8
        )
        self.shop_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure shop view grid
        for col in range(INVENTORY_COLUMNS):
            self.shop_view.grid_columnconfigure(col, weight=1)
        
        # View mode switcher
        self.shop_view_mode = ctk.StringVar(value="Tier")
        view_mode_frame = ctk.CTkFrame(self.shop_view, fg_color="transparent")
        view_mode_frame.grid(row=0, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(
            view_mode_frame,
            text="View:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_muted']
        ).pack(side="left", padx=(5, 10))
        
        self.view_mode_buttons = ctk.CTkSegmentedButton(
            view_mode_frame,
            values=VIEW_MODES,
            variable=self.shop_view_mode,
            command=self._on_view_mode_change,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            fg_color=self.colors['card_bg'],
            selected_color=self.colors['blurple'],
            selected_hover_color="#4752c4",
            unselected_color=self.colors['sidebar_bg'],
            unselected_hover_color=self.colors['text_muted']
        )
        self.view_mode_buttons.pack(side="left")
        
        # Container for inventory buttons
        self.inventory_container = ctk.CTkFrame(self.shop_view, fg_color="transparent")
        self.inventory_container.grid(row=1, column=0, columnspan=4, sticky="nsew")
        for col in range(INVENTORY_COLUMNS):
            self.inventory_container.grid_columnconfigure(col, weight=1)
        
        # Create inventory slots using builder
        self._create_inventory_slots()
        
        # Hide shop view by default
        self.shop_view.grid_remove()
    
    def _build_activity_log(self, parent):
        """Build the activity log section."""
        log_container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['card_bg'],
            corner_radius=10
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Header for Log
        ctk.CTkLabel(
            log_container,
            text="📝 Activity Log",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w", padx=15, pady=(8, 5))
        
        # Log textbox
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
    
    # =========================================================================
    # INVENTORY MANAGEMENT
    # =========================================================================
    
    def _create_inventory_slots(self):
        """Create interactive inventory button grid based on current view mode."""
        view_mode = self.shop_view_mode.get() if hasattr(self, 'shop_view_mode') else "Tier"
        self.inventory_builder.create_inventory_slots(
            self.inventory_container,
            view_mode,
            self.select_seed
        )
        
        # Initialize and update visuals
        self.seed_controller.initialize_selected_seeds()
        self.inventory_builder.update_button_visuals(config.Config.SELECTED_SEEDS)
    
    def _on_view_mode_change(self, mode):
        """Handle view mode change and rebuild inventory."""
        self._create_inventory_slots()
    
    def select_seed(self, seed_name):
        """Toggle seed selection for multi-buy."""
        self.seed_controller.select_seed(seed_name)
    
    # =========================================================================
    # TAB SWITCHING
    # =========================================================================
    
    def on_tab_change(self, selected_tab=None):
        """Handle tab switching to swap views and sidebar content."""
        current_tab = self.tab_view.get()
        
        if current_tab == "Shop":
            self.farm_view.grid_remove()
            self.shop_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.view_header_label.configure(text="🛒 SHOP INVENTORY")
            self.shop_stats_container.pack(fill="x")
        else:
            self.shop_view.grid_remove()
            self.farm_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.view_header_label.configure(text="🌱 LIVE FIELD")
            self.shop_stats_container.pack_forget()
    
    # =========================================================================
    # BOT CONTROL (delegated to controller)
    # =========================================================================
    
    def start_farming(self):
        """Start the bot in Farming Mode."""
        self.bot_controller.start_farming()
    
    def start_shopping_mode(self):
        """Start the bot in pure Shop Mode."""
        self.bot_controller.start_shopping_mode(
            self.seeds_per_trip_var,
            self.autobuy_interval_var
        )
    
    def stop_bot(self):
        """Stop the automation loop."""
        self.bot_controller.stop_bot()
    
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
    
    # =========================================================================
    # LOGGING
    # =========================================================================
    
    def log(self, message, tag="info"):
        """Add a timestamped message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n", tag)
        self.log_text.configure(state="disabled")
        
        if self.auto_scroll.get():
            self.log_text.see("end")
        
        self.root.update_idletasks()
    
    # =========================================================================
    # UI UPDATE LOOP
    # =========================================================================
    
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
        self.mini_map.update_position(
            state.current_position['row'], 
            state.current_position['col']
        )
        
        # Format Cycle Speed
        avg_time = self.get_avg_cycle_time()
        self.stat_labels['cycle_speed'].configure(text=f"{avg_time:.1f}s")
        
        # Update Next Buy timer
        if (state.bot_running and config.Config.AUTOBUY_ENABLED and 
            'last_buy_time' in state.stats):
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
            if self.status_label.current_status != "STOPPED":
                self.status_label.set_status("IDLE")
        
        # Update Shop Timer
        next_buy = state.stats.get('next_buy_time', 0)
        current_mode = getattr(self.bot_controller, 'current_mode', 'farm')
        if next_buy > 0 and state.bot_running and current_mode == 'shop':
            self.shop_timer_label.configure(text=f"Next Auto-Buy: {int(next_buy)}s")
        else:
            self.shop_timer_label.configure(text="Next Auto-Buy: --")
        
        # Schedule next update
        self.root.after(100, self.update_ui)
    
    # =========================================================================
    # CONFIGURATION (delegated to controller)
    # =========================================================================
    
    def _on_autobuy_toggle(self):
        """Update config when auto-buy toggle is changed."""
        config.Config.AUTOBUY_ENABLED = self.autobuy_enabled_var.get()
        config.Config.save()
        status = "enabled" if config.Config.AUTOBUY_ENABLED else "disabled"
        self.log(f"Auto-buy {status}.", "info")
    
    def _save_shop_settings(self):
        """Save shop settings to config."""
        self.config_controller.save_shop_settings(
            self.seeds_per_trip_var,
            self.autobuy_interval_var,
            self.shop_search_attempts_var
        )
    
    def save_config(self):
        """Save current configuration values."""
        self.config_controller.save_config(self.config_vars)
    
    def reset_configuration(self):
        """Reset all configuration values to safe defaults."""
        self.config_controller.reset_configuration(self.config_vars)
        self.log("Configuration reset to defaults.", "warning")
    
    def reset_stats(self):
        """Reset all statistics and position after confirmation."""
        self.config_controller.reset_stats(self.mini_map)
    
    def open_guide(self):
        """Open the Help & Guide window (singleton)."""
        if self.guide_window is None or not self.guide_window.winfo_exists():
            self.guide_window = GuideWindow(self.root, colors=self.colors)
        else:
            self.guide_window.focus_force()
    
    # =========================================================================
    # AUTO-UPDATE FUNCTIONALITY
    # =========================================================================
    
    def check_for_updates(self, silent: bool = False):
        """
        Check for updates from GitHub.
        
        Args:
            silent: If True, don't show dialogs unless update is available
        """
        # Update button text to show checking (for manual checks)
        if not silent:
            self.version_button.configure(text="⏳ Checking...")
            self.version_button.configure(state="disabled")
        
        # Check in background
        check_for_updates_async(
            lambda result: self.root.after(0, lambda: self._on_update_check_complete(result, silent))
        )
    
    def _on_update_check_complete(self, result: dict, silent: bool):
        """Handle update check completion."""
        # Restore button state
        self.version_button.configure(text=f"🔄 v{CURRENT_VERSION}")
        self.version_button.configure(state="normal")
        
        # Handle errors
        if result.get('error'):
            if not silent:
                self.log(f"Update check failed: {result['error']}", "warning")
                messagebox.showwarning(
                    "Update Check Failed",
                    f"Could not check for updates:\n{result['error']}"
                )
            return
        
        # No update available
        if not result.get('available'):
            if not silent:
                NoUpdateDialog(self.root, result['current_version'], colors=self.colors)
            return
        
        # Check if this version was skipped
        skipped = config.Config.UPDATE_SKIPPED_VERSION
        latest = result.get('latest_version', '')
        if silent and skipped and skipped == latest:
            self.log(f"Update {latest} available but skipped by user", "info")
            return
        
        # Show update dialog
        self._show_update_dialog(result)
    
    def _show_update_dialog(self, update_info: dict):
        """Show the update available dialog."""
        self.update_dialog = UpdateDialog(
            self.root,
            update_info,
            on_update=lambda: self._start_download(update_info),
            on_skip=self._on_skip_version,
            on_dismiss=lambda: None,
            colors=self.colors
        )
    
    def _on_skip_version(self, version: str):
        """Handle user skipping a version."""
        config.Config.UPDATE_SKIPPED_VERSION = version
        config.Config.save()
        self.log(f"Skipped update {version}", "info")
    
    def _start_download(self, update_info: dict):
        """Start downloading the update."""
        download_url = update_info.get('download_url')
        if not download_url:
            messagebox.showerror(
                "Download Error",
                "No download URL available for this release."
            )
            return
        
        self.log(f"Downloading update {update_info.get('latest_version')}...", "info")
        
        def on_progress(downloaded, total):
            # Update progress on main thread
            self.root.after(0, lambda: self.update_dialog.update_progress(downloaded, total))
        
        def on_complete(file_path):
            self.root.after(0, lambda: self._on_download_complete(file_path))
        
        download_update_async(download_url, on_progress, on_complete)
    
    def _on_download_complete(self, file_path: str):
        """Handle download completion."""
        if not file_path:
            if hasattr(self, 'update_dialog') and self.update_dialog.winfo_exists():
                self.update_dialog.show_download_error("Download failed")
            self.log("Update download failed", "error")
            return
        
        self.log("Download complete, applying update...", "success")
        
        if hasattr(self, 'update_dialog') and self.update_dialog.winfo_exists():
            self.update_dialog.show_download_complete()
        
        # Apply the update
        if apply_update(file_path):
            self.log("Update will be applied. Closing application...", "info")
            # Give user a moment to see the message
            self.root.after(1500, self._close_for_update)
        else:
            messagebox.showinfo(
                "Development Mode",
                "Running in development mode - update downloaded but not applied.\n"
                f"Downloaded to: {file_path}"
            )
    
    def _close_for_update(self):
        """Close the application for update."""
        try:
            self.root.destroy()
        except Exception:
            pass
    
    def check_for_updates_on_startup(self):
        """Check for updates on app startup (called after GUI is shown)."""
        if config.Config.AUTO_UPDATE_CHECK:
            # Small delay to let the app fully initialize
            self.root.after(2000, lambda: self.check_for_updates(silent=True))
