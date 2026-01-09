"""
Cross-platform input handler for the Magic Garden Bot.

This module provides platform-agnostic keyboard input functions:
- On Windows: Uses pydirectinput for DirectInput compatibility
- On Linux/macOS: Uses pynput as fallback

This ensures the bot can run on any operating system.
"""

import sys
import time

# Detect platform
IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    try:
        import pydirectinput
        _USE_DIRECTINPUT = True
    except ImportError:
        _USE_DIRECTINPUT = False
        print("WARNING: pydirectinput not found on Windows, falling back to pynput")
else:
    _USE_DIRECTINPUT = False

# Always import pynput as fallback
from pynput.keyboard import Controller, Key

_keyboard = Controller()


def key_down(key):
    """
    Press and hold a key.
    
    Args:
        key: Key to press (string like 'shift', 'space', or character)
    """
    if _USE_DIRECTINPUT:
        pydirectinput.keyDown(key)
    else:
        # Convert string keys to pynput Key objects
        key_obj = _convert_key(key)
        _keyboard.press(key_obj)


def key_up(key):
    """
    Release a key.
    
    Args:
        key: Key to release (string like 'shift', 'space', or character)
    """
    if _USE_DIRECTINPUT:
        pydirectinput.keyUp(key)
    else:
        key_obj = _convert_key(key)
        _keyboard.release(key_obj)


def press(key):
    """
    Press and release a key.
    
    Args:
        key: Key to press (string like 'escape', 'space', or character)
    """
    if _USE_DIRECTINPUT:
        pydirectinput.press(key)
    else:
        key_obj = _convert_key(key)
        _keyboard.press(key_obj)
        time.sleep(0.05)
        _keyboard.release(key_obj)


def _convert_key(key):
    """
    Convert string key names to pynput Key objects.
    
    Args:
        key: String key name or character
        
    Returns:
        pynput Key object or character
    """
    if isinstance(key, str):
        key_lower = key.lower()
        key_map = {
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'control': Key.ctrl,
            'alt': Key.alt,
            'space': Key.space,
            'enter': Key.enter,
            'return': Key.enter,
            'escape': Key.esc,
            'esc': Key.esc,
            'tab': Key.tab,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
        }
        return key_map.get(key_lower, key)
    return key


def get_platform_info():
    """
    Get information about the current input backend.
    
    Returns:
        str: Description of the active input backend
    """
    if _USE_DIRECTINPUT:
        return "pydirectinput (Windows DirectInput)"
    else:
        backend = "pynput"
        platform = "Windows" if IS_WINDOWS else ("Linux" if sys.platform.startswith('linux') else "macOS")
        return f"{backend} ({platform})"
