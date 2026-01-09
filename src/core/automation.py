"""
Core automation utilities for the Magic Garden Bot.

This module provides low-level automation functions including:
- Image template matching
- Keyboard input
- Screen capture
- Resource path resolution
"""

import pyautogui
import time
import sys
import os
from pynput.keyboard import Controller, Key

import numpy as np
from PIL import ImageGrab

from . import state
from .config import Config

# Failsafe - moving mouse to top-left corner will stop the script
pyautogui.FAILSAFE = True

# Keyboard controller
keyboard = Controller()

# Check for OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError as e:
    CV2_AVAILABLE = False
    print(f"WARNING: OpenCV (cv2) not found: {e}")
    print("Image detection features will not work properly.")


# =============================================================================
# RESOURCE PATH UTILITIES
# =============================================================================

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    
    # Development mode
    base_path = os.path.abspath(".")
    
    # Check direct path (e.g. if images/ is in root)
    path = os.path.join(base_path, relative_path)
    if os.path.exists(path):
        return path
        
    # Check inside src/ (e.g. if images/ is in src/images/)
    path_src = os.path.join(base_path, "src", relative_path)
    if os.path.exists(path_src):
        return path_src
        
    return path


# =============================================================================
# IMAGE MATCHING UTILITIES
# =============================================================================

def _capture_screen(bottom_half=False):
    """
    Capture the screen and return as numpy array.
    
    Args:
        bottom_half: If True, only capture bottom half of screen
        
    Returns:
        tuple: (screenshot_np, offset_y, offset_x)
    """
    try:
        # Try to capture all screens (works on Windows with multiple monitors)
        screenshot = ImageGrab.grab(all_screens=True)
    except Exception:
        # Fallback to default if all_screens not supported
        screenshot = ImageGrab.grab()
    
    screenshot_np = np.array(screenshot)
    
    if bottom_half:
        screen_height = screenshot_np.shape[0]
        screenshot_np = screenshot_np[screen_height // 2:, :, :]
        return screenshot_np, screen_height // 2, 0
    
    return screenshot_np, 0, 0


def _load_template(image_path, grayscale=True):
    """
    Load a template image for matching.
    
    Args:
        image_path: Path to the template image
        grayscale: If True, load as grayscale
        
    Returns:
        numpy.ndarray or None: Loaded template or None if failed
    """
    if not CV2_AVAILABLE:
        return None
    
    full_path = resource_path(image_path)
    mode = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    template = cv2.imread(full_path, mode)
    
    if template is None:
        print(f"ERROR: Could not load template image: {full_path}")
    
    return template


def _match_template(screenshot_np, template, grayscale=True, threshold=True):
    """
    Perform template matching on a screenshot.
    
    Args:
        screenshot_np: Screenshot as numpy array (RGB format)
        template: Template image as numpy array
        grayscale: If True, convert to grayscale
        threshold: If True, apply binary threshold for better matching
        
    Returns:
        tuple: (max_loc, max_val, template_shape)
            max_loc: (x, y) of best match
            max_val: Confidence score 0-1
            template_shape: (height, width) of template
    """
    # Convert to grayscale if needed
    if grayscale:
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        if threshold:
            _, screenshot_processed = cv2.threshold(screenshot_gray, 200, 255, cv2.THRESH_BINARY)
            _, template_processed = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
        else:
            screenshot_processed = screenshot_gray
            template_processed = template
    else:
        screenshot_processed = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        template_processed = template
    
    # Perform template matching
    result = cv2.matchTemplate(screenshot_processed, template_processed, cv2.TM_CCOEFF_NORMED)
    
    # Find the maximum match
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    return max_loc, max_val, template.shape[:2]


def locate_image(image, confidence, bottom_half=False, grayscale=True):
    """
    Locate an image on the screen using OpenCV template matching.
    
    Uses TM_CCOEFF_NORMED method which is more robust to brightness
    and color variations between different GPUs.
    
    Args:
        image: Path to the template image
        confidence: Minimum confidence threshold (0-1)
        bottom_half: If True, only search bottom half of screen
        grayscale: If True, use grayscale matching
        
    Returns:
        tuple or None: (left, top, width, height) or None if not found
    """
    if not CV2_AVAILABLE:
        print("ERROR: OpenCV not available. Cannot locate images.")
        return None
    
    try:
        # Load template
        template = _load_template(image, grayscale)
        if template is None:
            return None
        
        # Capture screen
        screenshot_np, offset_y, offset_x = _capture_screen(bottom_half)
        
        # Match template
        max_loc, max_val, (h, w) = _match_template(screenshot_np, template, grayscale)
        
        # Check confidence threshold
        if max_val >= confidence:
            return (max_loc[0] + offset_x, max_loc[1] + offset_y, w, h)
        
        return None
        
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error locating image {image}: {e}")
        return None


def locate_image_with_confidence(image, confidence, bottom_half=False, grayscale=True):
    """
    Locate an image on the screen and return both location and actual confidence value.
    
    This is useful for debugging to see what confidence score is actually achieved.
    
    Args:
        image: Path to the template image
        confidence: Minimum confidence threshold (0-1)
        bottom_half: If True, only search bottom half of screen
        grayscale: If True, use grayscale matching
        
    Returns:
        tuple: (location, actual_confidence)
            location: (left, top, width, height) or None
            actual_confidence: Best match confidence score
    """
    if not CV2_AVAILABLE:
        return None, 0.0
    
    try:
        # Load template
        template = _load_template(image, grayscale)
        if template is None:
            return None, 0.0
        
        # Capture screen
        screenshot_np, offset_y, offset_x = _capture_screen(bottom_half)
        
        # Match template
        max_loc, max_val, (h, w) = _match_template(screenshot_np, template, grayscale)
        
        # Return location if above threshold, always return confidence
        if max_val >= confidence:
            return (max_loc[0] + offset_x, max_loc[1] + offset_y, w, h), max_val
        
        return None, max_val
        
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error locating image {image}: {e}")
        return None, 0.0


# =============================================================================
# IMAGE DETECTION CHECKS
# =============================================================================

def check_inventory_full():
    """
    Check if the inventory full popup appears.
    
    Uses grayscale matching and lower confidence threshold to handle
    color rendering differences between different GPUs (NVIDIA vs AMD).
    
    Returns:
        bool: True if inventory full popup detected
    """
    state.stats['inventory_checks'] += 1
    image_path = os.path.join(Config.IMAGE_FOLDER, "inventory_full.png")
    
    # Use lower confidence and grayscale to handle GPU color variations
    result, actual_confidence = locate_image_with_confidence(
        image_path, 
        confidence=Config.INVENTORY_CONFIDENCE, 
        grayscale=True
    )
    
    # Only print when detected (not on every check to avoid spam)
    if result is not None:
        print(f"✓ Inventory full detected! (match: {actual_confidence:.3f})")
    
    return result is not None


def check_harvest_button():
    """
    Check if the harvest button appears.
    
    Returns:
        bool: True if harvest button detected
    """
    image_path = os.path.join(Config.IMAGE_FOLDER, "harvest_button.png")
    return locate_image(image_path, confidence=Config.CONFIDENCE, grayscale=True) is not None


# =============================================================================
# INPUT UTILITIES
# =============================================================================

def click_region(region):
    """
    Click on the center of a given region.
    
    Args:
        region: (left, top, width, height) tuple or None
    """
    if region is None:
        return
    
    try:
        x, y = pyautogui.center(region)
        pyautogui.click(x, y)
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error clicking region: {e}")


def press_key(key, hold=0.05):
    """
    Press and release a single key.
    
    Args:
        key: Key to press (pynput Key or character)
        hold: How long to hold the key in seconds
    """
    try:
        keyboard.press(key)
        time.sleep(hold)
        keyboard.release(key)
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error pressing key {key}: {e}")


def press_hotkey(key1, key2, delay=0.5):
    """
    Press and release a hotkey combination (e.g., Shift + 2).
    
    Args:
        key1: First key (modifier)
        key2: Second key
        delay: Delay after releasing keys
    """
    try:
        keyboard.press(key1)
        keyboard.press(key2)
        time.sleep(0.05)
        keyboard.release(key2)
        keyboard.release(key1)
        time.sleep(delay)
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error pressing hotkey {key1} + {key2}: {e}")
