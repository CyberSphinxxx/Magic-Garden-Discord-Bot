# Centralized bot state management

# Statistics tracking dictionary
stats = {
    'total_harvests': 0,
    'total_sells': 0,
    'total_moves': 0,
    'start_time': None,
    'last_sell_time': None,
    'errors': 0,
    'inventory_checks': 0,
    'cycles': 0,
    'cycle_times': []
}

# Real-time position tracking
current_position = {'row': 0, 'col': 0}

# Bot operational flags
bot_running = False
bot_paused = False
