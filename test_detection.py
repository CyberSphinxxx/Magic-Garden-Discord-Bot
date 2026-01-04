"""
Quick test script to debug inventory detection.
Run this while the inventory full notification is visible on screen.
"""
import cv2
import numpy as np
from PIL import ImageGrab
import os
import time

# Path to template
template_path = "src/images/inventory_full.png"

# Load template
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
if template is None:
    print(f"ERROR: Could not load template from {template_path}")
    exit(1)

print(f"Template loaded: {template.shape[1]}x{template.shape[0]} pixels")

# Countdown before capture
print("\nGet ready! Capturing screenshot in...")
for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)
print("  Capturing NOW!")

# Capture screen - capture ALL monitors to match bot behavior
try:
    screenshot = ImageGrab.grab(all_screens=True)
except:
    screenshot = ImageGrab.grab()
screenshot_np = np.array(screenshot)
screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

print(f"Screenshot captured: {screenshot_gray.shape[1]}x{screenshot_gray.shape[0]} pixels")

# Try different matching methods
methods = {
    'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
    'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
    'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED,
}

print("\n" + "="*60)
print("TESTING DIFFERENT MATCHING METHODS")
print("="*60)

for method_name, method in methods.items():
    result = cv2.matchTemplate(screenshot_gray, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # For SQDIFF, lower is better; for others, higher is better
    if method == cv2.TM_SQDIFF_NORMED:
        match_val = 1 - min_val  # Convert to "higher is better"
        print(f"\n{method_name}:")
        print(f"  Best match: {match_val:.4f} (1 = perfect)")
        print(f"  Location: {min_loc}")
    else:
        print(f"\n{method_name}:")
        print(f"  Best match: {max_val:.4f} (1 = perfect)")
        print(f"  Location: {max_loc}")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)

# Use TM_CCOEFF_NORMED result
result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

print(f"\nBest confidence score: {max_val:.4f}")

if max_val >= 0.8:
    print("✓ Detection will work with standard threshold (0.8)")
elif max_val >= 0.6:
    print(f"⚠ Set INVENTORY_CONFIDENCE = {max_val - 0.05:.2f}")
elif max_val >= 0.4:
    print(f"⚠ Set INVENTORY_CONFIDENCE = {max_val - 0.05:.2f}")
    print("  (This is quite low - consider retaking template screenshot)")
else:
    print("✗ Match too low! Template image might not match current screen.")
    print("  Please verify:")
    print("  1. The inventory notification is currently visible")
    print("  2. The template image matches what's on screen")
    print("  3. Try taking a new screenshot for the template")

print("\n")
