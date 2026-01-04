import pyautogui
import time
import sys
import os
from pynput.keyboard import Controller, Key

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

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def locate_image(image, confidence, bottom_half=False, grayscale=True):
    """
    Locate an image on the screen using OpenCV template matching.
    
    Uses TM_CCOEFF_NORMED method which is more robust to brightness
    and color variations between different GPUs.
    """
    if not CV2_AVAILABLE:
        print("ERROR: OpenCV not available. Cannot locate images.")
        return None
    
    try:
        import numpy as np
        from PIL import ImageGrab
        
        image_path = resource_path(image)
        
        # Load template image
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
        if template is None:
            print(f"ERROR: Could not load template image: {image_path}")
            return None
        
        # Capture screen - use all_screens=True to capture ALL monitors
        # This fixes issues when using multiple monitors with different GPUs
        try:
            # Try to capture all screens (works on Windows with multiple monitors)
            screenshot = ImageGrab.grab(all_screens=True)
        except:
            # Fallback to default if all_screens not supported
            screenshot = ImageGrab.grab()
        
        # Get actual screenshot dimensions (might be larger than pyautogui.size() with multiple monitors)
        screenshot_np = np.array(screenshot)
        
        # Handle bottom_half region if requested
        if bottom_half:
            screen_height = screenshot_np.shape[0]
            screenshot_np = screenshot_np[screen_height // 2:, :, :]
            offset_y = screen_height // 2
            offset_x = 0
        else:
            offset_y = 0
            offset_x = 0
        
        # Convert to grayscale if needed
        if grayscale:
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        else:
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Perform template matching using TM_CCOEFF_NORMED (more robust to brightness/color variations)
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        
        # Find the maximum match value
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Check if match confidence is above threshold
        if max_val >= confidence:
            # Get template dimensions
            h, w = template.shape[:2]
            
            # Return in pyautogui format: (left, top, width, height)
            return (max_loc[0] + offset_x, max_loc[1] + offset_y, w, h)
        else:
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
    """
    if not CV2_AVAILABLE:
        return None, 0.0
    
    try:
        import numpy as np
        from PIL import ImageGrab
        
        image_path = resource_path(image)
        
        # Load template image
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
        if template is None:
            print(f"ERROR: Could not load template image: {image_path}")
            return None, 0.0
        
        # Capture screen - use all_screens=True to capture ALL monitors
        try:
            screenshot = ImageGrab.grab(all_screens=True)
        except:
            screenshot = ImageGrab.grab()
        
        # Get actual screenshot dimensions
        screenshot_np = np.array(screenshot)
        
        # Handle bottom_half region if requested
        if bottom_half:
            screen_height = screenshot_np.shape[0]
            screenshot_np = screenshot_np[screen_height // 2:, :, :]
            offset_y = screen_height // 2
            offset_x = 0
        else:
            offset_y = 0
            offset_x = 0
        
        # Convert to grayscale if needed
        if grayscale:
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        else:
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Perform template matching using TM_CCOEFF_NORMED
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        
        # Find the maximum match value
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Check if match confidence is above threshold
        if max_val >= confidence:
            # Get template dimensions
            h, w = template.shape[:2]
            
            # Return location and actual confidence
            return (max_loc[0] + offset_x, max_loc[1] + offset_y, w, h), max_val
        else:
            # Return None for location but still return the best match value
            return None, max_val
            
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error locating image {image}: {e}")
        return None, 0.0

def check_inventory_full():
    """
    Check if the inventory full popup appears.
    
    Uses grayscale matching and lower confidence threshold to handle
    color rendering differences between different GPUs (NVIDIA vs AMD).
    """
    state.stats['inventory_checks'] += 1
    image_path = os.path.join(Config.IMAGE_FOLDER, "inventory_full.png")
    
    # Use lower confidence and grayscale to handle GPU color variations
    # We'll also get the actual match value for debugging
    result, actual_confidence = locate_image_with_confidence(image_path, confidence=Config.INVENTORY_CONFIDENCE, grayscale=True)
    
    # Debug output with actual match score
    if result is not None:
        print(f"✓ Inventory full detected! (match: {actual_confidence:.3f}, threshold: {Config.INVENTORY_CONFIDENCE})")
    else:
        print(f"✗ Inventory check #{state.stats['inventory_checks']} - Not detected (best match: {actual_confidence:.3f}, threshold: {Config.INVENTORY_CONFIDENCE})")
    
    return result is not None


def check_harvest_button():
    """Check if the harvest button appears."""
    image_path = os.path.join(Config.IMAGE_FOLDER, "harvest_button.png")
    # Use grayscale to handle GPU color variations
    return locate_image(image_path, confidence=Config.CONFIDENCE, grayscale=True) is not None


def press_key(key, hold=0.05):
    """Press and release a single key."""
    try:
        keyboard.press(key)
        time.sleep(hold)
        keyboard.release(key)
    except Exception as e:
        state.stats['errors'] += 1
        print(f"Error pressing key {key}: {e}")

def press_hotkey(key1, key2, delay=0.5):
    """Press and release a hotkey combination (e.g., Shift + 2)."""
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
