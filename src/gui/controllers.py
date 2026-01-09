"""
Controller classes for the Magic Garden Bot GUI.

This module handles bot control logic and configuration management,
separating business logic from UI concerns.
"""

import threading
import time
from tkinter import messagebox

from src.core import state, config, game_actions
from src.gui.constants import DEFAULT_CONFIGS


class BotController:
    """
    Handles bot start/stop and automation thread management.
    
    This controller manages the bot's running state, threading,
    and delegates to the appropriate game action loops.
    """
    
    def __init__(self, gui_ref):
        """
        Initialize the bot controller.
        
        Args:
            gui_ref: Reference to the main GUI instance for callbacks
        """
        self.gui = gui_ref
        self.current_mode = 'farm'
    
    def start_farming(self):
        """Start the bot in Farming Mode (Harvesting)."""
        config.Config.HARVESTING_ENABLED = True
        config.Config.save()
        self.gui.log("Starting Farming Mode...", "info")
        self.start_bot(mode='farm')
    
    def start_shopping_mode(self, seeds_per_trip_var, autobuy_interval_var):
        """
        Start the bot in pure Shop Mode (Auto-Buy Only).
        
        Args:
            seeds_per_trip_var: StringVar containing seeds per trip value
            autobuy_interval_var: StringVar containing autobuy interval value
        """
        # Disable harvesting, enable autobuy for shop mode
        config.Config.HARVESTING_ENABLED = False
        config.Config.AUTOBUY_ENABLED = True
        
        # Save shop settings from UI
        try:
            config.Config.SEEDS_PER_TRIP = int(seeds_per_trip_var.get())
        except (ValueError, AttributeError):
            config.Config.SEEDS_PER_TRIP = 1
        
        try:
            config.Config.AUTOBUY_INTERVAL = int(autobuy_interval_var.get())
        except (ValueError, AttributeError):
            config.Config.AUTOBUY_INTERVAL = 180
        
        config.Config.save()
        seeds_count = len(config.Config.SELECTED_SEEDS)
        self.gui.log(
            f"Starting Shop Mode: {seeds_count} seed type(s), "
            f"{config.Config.SEEDS_PER_TRIP} each...", 
            "info"
        )
        self.start_bot(mode='shop')
    
    def start_bot(self, mode='farm'):
        """
        Start the automation loop in a separate thread.
        
        Args:
            mode: 'farm' for harvesting loop, 'shop' for dedicated shop loop
        """
        if state.bot_running:
            return
        
        self.current_mode = mode
        state.bot_running = True
        state.stats['start_time'] = time.time()
        self.gui.update_button_states()
        
        # Start automation in a background thread
        thread = threading.Thread(target=self._run_automation, daemon=True)
        thread.start()
        
        self.gui.status_label.set_status("RUNNING")
        self.gui.log("Automation started.", "success")
    
    def stop_bot(self):
        """Stop the automation loop."""
        if not state.bot_running:
            return
        
        state.bot_running = False
        self.gui.update_button_states()
        
        self.gui.status_label.set_status("STOPPING...")
        self.gui.log("Stopping automation...", "warning")
    
    def _run_automation(self):
        """Main bot loop executed in a separate thread."""
        time.sleep(3)  # Grace period for user to switch to game window
        
        if self.current_mode == 'shop':
            # Dedicated shop-only loop
            self.gui.log("Starting Shop Mode loop...", "success")
            game_actions.run_shop_only_loop(logger=self.gui.log)
            return
        
        # Farm mode - original harvest loop behavior
        self.gui.log("Starting Farming loop...", "success")
        
        while state.bot_running:
            try:
                state.stats['cycles'] += 1
                if state.bot_running:
                    # Calculate cycle duration
                    cycle_start = time.time()
                    self.gui.log(f"━━━ Cycle #{state.stats['cycles']} started ━━━", "info")
                    
                    game_actions.harvest_loop(logger=self.gui.log)
                    
                    # Record duration
                    duration = time.time() - cycle_start
                    state.stats['cycle_times'].append(duration)
                    # Keep only the last 10
                    state.stats['cycle_times'] = state.stats['cycle_times'][-10:]
                    
                    self.gui.log(
                        f"✓ Cycle #{state.stats['cycles']} complete! ({duration:.1f}s)", 
                        "success"
                    )
                    if config.Config.LOOP_COOLDOWN > 0:
                        self.gui.log(
                            f"Waiting {config.Config.LOOP_COOLDOWN}s before next cycle...", 
                            "info"
                        )
                    time.sleep(config.Config.LOOP_COOLDOWN)
                    
            except Exception as e:
                self.gui.log(f"An unexpected error occurred in bot thread: {e}", "error")
                state.stats['errors'] += 1
                time.sleep(2)


class ConfigController:
    """
    Handles configuration CRUD operations.
    
    This controller manages saving, loading, and resetting
    configuration values.
    """
    
    def __init__(self, gui_ref):
        """
        Initialize the config controller.
        
        Args:
            gui_ref: Reference to the main GUI instance for callbacks
        """
        self.gui = gui_ref
    
    def save_config(self, config_vars):
        """
        Save current configuration values.
        
        Args:
            config_vars: Dictionary of {config_key: StringVar}
        """
        try:
            for key, var in config_vars.items():
                str_value = var.get().strip()
                if str_value == "":
                    self.gui.log(f"Config error: {key} is empty.", "error")
                    return
                value = float(str_value)
                # Convert to int if it's a whole number
                setattr(config.Config, key, int(value) if value.is_integer() else value)
            config.Config.save()
            self.gui.log("Configuration saved!", "success")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except ValueError:
            self.gui.log("Config error: Invalid number format.", "error")
            messagebox.showerror(
                "Error", 
                "Invalid configuration value. Please enter numbers only."
            )
    
    def save_shop_settings(self, seeds_per_trip_var, autobuy_interval_var, 
                           shop_search_attempts_var):
        """
        Save shop settings to config.
        
        Args:
            seeds_per_trip_var: StringVar for seeds per trip
            autobuy_interval_var: StringVar for autobuy interval
            shop_search_attempts_var: StringVar for search attempts
        """
        try:
            # Save seeds per trip
            seeds_per_trip = int(seeds_per_trip_var.get())
            if seeds_per_trip < 1:
                seeds_per_trip = 1
            config.Config.SEEDS_PER_TRIP = seeds_per_trip
            
            # Save autobuy interval
            autobuy_interval = int(autobuy_interval_var.get())
            if autobuy_interval < 10:
                autobuy_interval = 10  # Minimum 10 seconds
            config.Config.AUTOBUY_INTERVAL = autobuy_interval
            
            # Save search attempts
            search_attempts = int(shop_search_attempts_var.get())
            if search_attempts < 1:
                search_attempts = 1
            config.Config.SHOP_SEARCH_ATTEMPTS = search_attempts
            
            # Save to disk
            config.Config.save()
            
            self.gui.log(
                f"✓ Shop settings saved: {seeds_per_trip} seeds/trip, "
                f"{autobuy_interval}s interval, {search_attempts} attempts", 
                "success"
            )
        except ValueError:
            self.gui.log("⚠️ Invalid shop settings - please enter numbers only.", "error")
    
    def reset_configuration(self, config_vars):
        """
        Reset all configuration values to safe defaults.
        
        Args:
            config_vars: Dictionary of {config_key: StringVar}
        """
        for key, default_value in DEFAULT_CONFIGS.items():
            if key in config_vars:
                config_vars[key].set(default_value)
        self.gui.log("Configuration reset to defaults.", "warning")
    
    def reset_stats(self, mini_map):
        """
        Reset all statistics and position after confirmation.
        
        Args:
            mini_map: MiniMapWidget reference to update position display
        """
        if messagebox.askyesno(
            "Reset Farm Loop", 
            "This will reset all statistics and position.\n\n"
            "After resetting, move your character to the TOP-LEFT corner "
            "(Tile 0,0) before starting again.\n\nContinue?"
        ):
            for key in ['total_harvests', 'total_sells', 'total_moves', 
                        'errors', 'inventory_checks', 'cycles']:
                state.stats[key] = 0
            state.stats['start_time'] = None
            
            # Reset position to start
            state.current_position['row'] = 0
            state.current_position['col'] = 0
            mini_map.update_position(0, 0)
            
            self.gui.log(
                "🔄 Farm loop reset! Move character to TOP-LEFT corner before starting.", 
                "warning"
            )


class SeedController:
    """
    Handles seed selection and state management.
    
    This controller manages the multi-seed selection logic
    and visual state updates.
    """
    
    def __init__(self, gui_ref, inventory_builder):
        """
        Initialize the seed controller.
        
        Args:
            gui_ref: Reference to the main GUI instance
            inventory_builder: InventoryBuilder instance for visual updates
        """
        self.gui = gui_ref
        self.inventory_builder = inventory_builder
    
    def select_seed(self, seed_name):
        """
        Toggle seed selection for multi-buy.
        
        Args:
            seed_name: Name of the seed to toggle
        """
        # Initialize SELECTED_SEEDS if it doesn't exist (backward compatibility)
        if not hasattr(config.Config, 'SELECTED_SEEDS') or config.Config.SELECTED_SEEDS is None:
            config.Config.SELECTED_SEEDS = []
        
        # Toggle selection
        if seed_name in config.Config.SELECTED_SEEDS:
            config.Config.SELECTED_SEEDS.remove(seed_name)
            action = "Deselected"
        else:
            config.Config.SELECTED_SEEDS.append(seed_name)
            action = "Selected"
        
        # Update legacy SELECTED_SEED to first in list (or empty)
        if config.Config.SELECTED_SEEDS:
            config.Config.SELECTED_SEED = config.Config.SELECTED_SEEDS[0]
        
        config.Config.save()
        
        # Update button visuals
        self.inventory_builder.update_button_visuals(config.Config.SELECTED_SEEDS)
        
        # Log selection
        if hasattr(self.gui, 'log_text'):
            count = len(config.Config.SELECTED_SEEDS)
            self.gui.log(f"{action} {seed_name}. Total seeds selected: {count}", "info")
    
    def initialize_selected_seeds(self):
        """Initialize SELECTED_SEEDS from legacy SELECTED_SEED if needed."""
        if not hasattr(config.Config, 'SELECTED_SEEDS') or not config.Config.SELECTED_SEEDS:
            config.Config.SELECTED_SEEDS = (
                [config.Config.SELECTED_SEED] if config.Config.SELECTED_SEED else []
            )
