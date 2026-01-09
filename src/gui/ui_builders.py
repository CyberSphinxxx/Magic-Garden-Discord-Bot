"""
UI Builder classes and factory functions for the Magic Garden Bot GUI.

This module provides reusable components for constructing the GUI,
reducing code duplication and improving maintainability.
"""

import customtkinter as ctk
from src.gui.constants import (
    UI_COLORS, SEED_TIERS, ALL_SEEDS, CONFIG_DEFINITIONS,
    INVENTORY_COLUMNS, VIEW_MODES, get_seed_color_map,
    FONT_FAMILY, FONT_MONO
)
from src.gui.tooltip import ToolTip
from src.core import config


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_stat_box(parent, label, key, col, colors, stat_labels_dict):
    """
    Create a single stat display box with value as hero element.
    
    Args:
        parent: Parent widget
        label: Display label for the stat
        key: Key for the stat_labels dictionary
        col: Column position in grid
        colors: Color palette dictionary
        stat_labels_dict: Dictionary to store label references
        
    Returns:
        CTkFrame: The created stat box frame
    """
    box = ctk.CTkFrame(parent, fg_color=colors['sidebar_bg'], corner_radius=8)
    box.grid(row=0, column=col, padx=3, pady=2, sticky="ew")
    
    # Value (Hero) - Large, bold, bright white, centered
    value_label = ctk.CTkLabel(
        box,
        text="0",
        font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
        text_color=colors['text_primary']
    )
    value_label.pack(pady=(12, 0))
    stat_labels_dict[key] = value_label
    
    # Label (Secondary) - Small, muted grey, below the value
    ctk.CTkLabel(
        box,
        text=label,
        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
        text_color="gray70"
    ).pack(pady=(2, 10))
    
    return box


def create_config_row(parent, label_text, var, tooltip_text, colors):
    """
    Create a configuration row with label and entry field.
    
    Args:
        parent: Parent widget
        label_text: Text for the label
        var: StringVar for the entry
        tooltip_text: Tooltip help text
        colors: Color palette dictionary
        
    Returns:
        CTkFrame: The created row frame
    """
    row_frame = ctk.CTkFrame(parent, fg_color="transparent")
    row_frame.pack(fill="x", pady=3)
    
    ctk.CTkLabel(
        row_frame,
        text=label_text,
        font=ctk.CTkFont(family=FONT_FAMILY, size=11),
        text_color=colors['text_secondary'],
        width=120,
        anchor="w"
    ).pack(side="left")
    
    entry = ctk.CTkEntry(
        row_frame,
        textvariable=var,
        width=80,
        height=28,
        font=ctk.CTkFont(family=FONT_MONO, size=11),
        fg_color=colors['window_bg'],
        border_color=colors['blurple'],
        corner_radius=6
    )
    entry.pack(side="right")
    ToolTip(entry, tooltip_text)
    
    return row_frame


def create_control_button(parent, text, command, fg_color, hover_color, 
                          width=60, height=40, state="normal"):
    """
    Create a styled control button.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button command callback
        fg_color: Foreground/background color
        hover_color: Hover state color
        width: Button width
        height: Button height
        state: Button state ("normal" or "disabled")
        
    Returns:
        CTkButton: The created button
    """
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=fg_color,
        hover_color=hover_color,
        font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
        height=height,
        width=width,
        corner_radius=10,
        state=state
    )


# =============================================================================
# INVENTORY BUILDER
# =============================================================================

class InventoryBuilder:
    """Handles seed inventory grid creation and management."""
    
    def __init__(self, colors):
        """
        Initialize the inventory builder.
        
        Args:
            colors: UI color palette dictionary
        """
        self.colors = colors
        self.seed_colors = get_seed_color_map()
        self.shop_buttons = {}
    
    def create_inventory_slots(self, container, view_mode, select_callback):
        """
        Create interactive inventory button grid based on current view mode.
        
        Args:
            container: Parent container widget
            view_mode: Current view mode ("Grid", "Tier", or "A-Z")
            select_callback: Callback function when seed is selected
            
        Returns:
            dict: Dictionary of {seed_name: [button_list]}
        """
        # Clear existing buttons
        for widget in container.winfo_children():
            widget.destroy()
        self.shop_buttons = {}
        
        cols = INVENTORY_COLUMNS
        current_row = 0
        
        if view_mode == "Grid":
            self._create_grid_layout(container, cols, select_callback)
        elif view_mode == "A-Z":
            self._create_alphabetical_layout(container, cols, select_callback)
        else:  # Tier view (default)
            self._create_tier_layout(container, cols, select_callback)
        
        return self.shop_buttons
    
    def _create_grid_layout(self, container, cols, select_callback):
        """Create simple grid layout."""
        for idx, seed_name in enumerate(ALL_SEEDS):
            row = idx // cols
            col = idx % cols
            button = self._create_seed_button(container, seed_name, select_callback)
            button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            self.shop_buttons[seed_name] = [button]
    
    def _create_alphabetical_layout(self, container, cols, select_callback):
        """Create alphabetically sorted layout."""
        sorted_seeds = sorted(ALL_SEEDS)
        for idx, seed_name in enumerate(sorted_seeds):
            row = idx // cols
            col = idx % cols
            button = self._create_seed_button(container, seed_name, select_callback)
            button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            self.shop_buttons[seed_name] = [button]
    
    def _create_tier_layout(self, container, cols, select_callback):
        """Create tier-grouped layout with headers."""
        current_row = 0
        
        for tier_name, tier_color, seeds in SEED_TIERS:
            # Tier header label
            tier_label = ctk.CTkLabel(
                container,
                text=f"━━━ {tier_name} ━━━",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=tier_color
            )
            tier_label.grid(row=current_row, column=0, columnspan=cols, 
                          pady=(10, 5), sticky="ew")
            current_row += 1
            
            # Seed buttons for this tier
            for idx, seed_name in enumerate(seeds):
                col = idx % cols
                if idx > 0 and col == 0:
                    current_row += 1
                
                button = self._create_seed_button(container, seed_name, select_callback)
                button.grid(row=current_row, column=col, padx=3, pady=2, sticky="nsew")
                self.shop_buttons[seed_name] = [button]
            
            current_row += 1
    
    def _create_seed_button(self, parent, seed_name, select_callback):
        """
        Create a single seed button widget.
        
        Args:
            parent: Parent widget
            seed_name: Name of the seed
            select_callback: Callback when button is clicked
            
        Returns:
            CTkButton: The created seed button
        """
        seed_color = self.seed_colors.get(seed_name, "gray")
        
        return ctk.CTkButton(
            parent,
            text=seed_name,
            width=100,
            height=40,
            fg_color="transparent",
            hover_color=self.colors['card_bg'],
            border_width=2,
            border_color=seed_color,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=self.colors['text_secondary'],
            corner_radius=8,
            command=lambda s=seed_name: select_callback(s)
        )
    
    def update_button_visuals(self, selected_seeds):
        """
        Update all seed button visuals based on selection state.
        
        Args:
            selected_seeds: List of currently selected seed names
        """
        for name, buttons in self.shop_buttons.items():
            seed_color = self.seed_colors.get(name, "gray")
            
            for button in buttons:
                if name in selected_seeds:
                    # Selected state - Rarity color background (Solid)
                    text_color = "#FFFFFF"
                    # Improve text color for very light backgrounds
                    if seed_color.upper() in ["#FFFFFF", "#F39C12", "#00CED1"]:
                        text_color = "#000000"
                    
                    button.configure(
                        fg_color=seed_color,
                        border_color=seed_color,
                        text_color=text_color
                    )
                else:
                    # Unselected state - transparent with Rarity border
                    button.configure(
                        fg_color="transparent",
                        border_color=seed_color,
                        text_color=self.colors['text_secondary']
                    )


# =============================================================================
# STATISTICS PANEL BUILDER
# =============================================================================

class StatisticsPanelBuilder:
    """Builds the statistics panel with all stat boxes."""
    
    def __init__(self, colors):
        """
        Initialize the statistics panel builder.
        
        Args:
            colors: UI color palette dictionary
        """
        self.colors = colors
        self.stat_labels = {}
    
    def build(self, parent):
        """
        Build the complete statistics panel.
        
        Args:
            parent: Parent widget
            
        Returns:
            dict: Dictionary of stat label references
        """
        # Header
        ctk.CTkLabel(
            parent,
            text="📊 STATISTICS",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=self.colors['text_muted']
        ).pack(anchor="w", pady=(5, 5))
        
        stats_frame = ctk.CTkFrame(parent, fg_color=self.colors['card_bg'], corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Row 1: Cycles, Runtime, Cycle Speed
        row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=10)
        row1.grid_columnconfigure((0, 1, 2), weight=1)
        
        create_stat_box(row1, "Cycles", "cycles", 0, self.colors, self.stat_labels)
        create_stat_box(row1, "Runtime", "runtime", 1, self.colors, self.stat_labels)
        create_stat_box(row1, "Cycle Speed", "cycle_speed", 2, self.colors, self.stat_labels)
        
        # Row 2: Harvests, Sells, Moves
        row2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 10))
        row2.grid_columnconfigure((0, 1, 2), weight=1)
        
        create_stat_box(row2, "Harvests", "total_harvests", 0, self.colors, self.stat_labels)
        create_stat_box(row2, "Sells", "total_sells", 1, self.colors, self.stat_labels)
        create_stat_box(row2, "Moves", "total_moves", 2, self.colors, self.stat_labels)
        
        # Row 3: Errors and Next Buy
        row3 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 10))
        row3.grid_columnconfigure((0, 1), weight=1)
        
        create_stat_box(row3, "Errors", "errors", 0, self.colors, self.stat_labels)
        create_stat_box(row3, "Next Buy", "next_buy", 1, self.colors, self.stat_labels)
        
        return self.stat_labels


# =============================================================================
# CONFIGURATION PANEL BUILDER
# =============================================================================

class ConfigurationPanelBuilder:
    """Builds the farm configuration panel."""
    
    def __init__(self, colors):
        """
        Initialize the configuration panel builder.
        
        Args:
            colors: UI color palette dictionary
        """
        self.colors = colors
        self.config_vars = {}
    
    def build(self, parent, autobuy_var, autobuy_callback, save_callback):
        """
        Build the configuration panel.
        
        Args:
            parent: Parent widget (CollapsibleFrame content)
            autobuy_var: BooleanVar for autobuy toggle
            autobuy_callback: Callback when autobuy is toggled
            save_callback: Callback when save button is clicked
            
        Returns:
            dict: Dictionary of config StringVars
        """
        config_inner = ctk.CTkFrame(parent, fg_color="transparent")
        config_inner.pack(fill="x", padx=10, pady=10)
        
        # Enable Shopping Toggle
        shopping_toggle = ctk.CTkSwitch(
            config_inner,
            text="Enable Shopping",
            variable=autobuy_var,
            command=autobuy_callback,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            button_color=self.colors['blurple'],
            progress_color=self.colors['blurple']
        )
        shopping_toggle.pack(fill="x", padx=0, pady=(0, 10))
        ToolTip(shopping_toggle, "Enable automatic transitions to Shop mode for buying seeds.")
        
        # Config entries
        for label_text, config_key, min_val, max_val, tooltip_text in CONFIG_DEFINITIONS:
            var = ctk.StringVar(value=str(getattr(config.Config, config_key)))
            self.config_vars[config_key] = var
            create_config_row(config_inner, label_text, var, tooltip_text, self.colors)
        
        # Save Config Button
        save_btn = ctk.CTkButton(
            config_inner,
            text="💾 Save Configuration",
            command=save_callback,
            fg_color=self.colors['blurple'],
            hover_color="#4752c4",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            height=36,
            corner_radius=8
        )
        save_btn.pack(fill="x", pady=(15, 0))
        
        return self.config_vars


# =============================================================================
# SHOP SETTINGS BUILDER
# =============================================================================

class ShopSettingsBuilder:
    """Builds the shop settings panel."""
    
    def __init__(self, colors):
        """
        Initialize the shop settings builder.
        
        Args:
            colors: UI color palette dictionary
        """
        self.colors = colors
        self.seeds_per_trip_var = None
        self.autobuy_interval_var = None
        self.shop_search_attempts_var = None
    
    def build(self, parent, save_callback):
        """
        Build the shop settings panel.
        
        Args:
            parent: Parent widget (CollapsibleFrame content)
            save_callback: Callback when save button is clicked
            
        Returns:
            tuple: (seeds_per_trip_var, autobuy_interval_var, shop_search_attempts_var)
        """
        shop_inner = ctk.CTkFrame(parent, fg_color="transparent")
        shop_inner.pack(fill="x", padx=10, pady=10)
        
        # Seeds Per Trip
        self.seeds_per_trip_var = ctk.StringVar(
            value=str(getattr(config.Config, 'SEEDS_PER_TRIP', 1))
        )
        self._create_setting_row(
            shop_inner, "Seeds Per Trip", self.seeds_per_trip_var,
            "Number of each selected seed to buy per shop visit."
        )
        
        # Shop Interval
        self.autobuy_interval_var = ctk.StringVar(
            value=str(config.Config.AUTOBUY_INTERVAL)
        )
        self._create_setting_row(
            shop_inner, "Interval (seconds)", self.autobuy_interval_var,
            "Time between shop visits in seconds (default: 180)."
        )
        
        # Search Attempts
        self.shop_search_attempts_var = ctk.StringVar(
            value=str(getattr(config.Config, 'SHOP_SEARCH_ATTEMPTS', 7))
        )
        self._create_setting_row(
            shop_inner, "Search Attempts", self.shop_search_attempts_var,
            "Number of scroll attempts to find each seed (default: 7)."
        )
        
        # Save Button
        save_btn_row = ctk.CTkFrame(shop_inner, fg_color="transparent")
        save_btn_row.pack(fill="x", pady=(10, 5))
        
        ctk.CTkButton(
            save_btn_row,
            text="💾 Save Settings",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color=self.colors['green'],
            hover_color="#1E7D32",
            corner_radius=8,
            height=32,
            command=save_callback
        ).pack(fill="x")
        
        return (self.seeds_per_trip_var, self.autobuy_interval_var, 
                self.shop_search_attempts_var)
    
    def _create_setting_row(self, parent, label_text, var, tooltip_text):
        """Create a settings row with label and entry."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=self.colors['text_secondary'],
            width=140,
            anchor="w"
        ).pack(side="left")
        
        entry = ctk.CTkEntry(
            row,
            textvariable=var,
            width=80,
            height=28,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            fg_color=self.colors['window_bg'],
            border_color=self.colors['blurple'],
            corner_radius=6
        )
        entry.pack(side="right")
        ToolTip(entry, tooltip_text)
