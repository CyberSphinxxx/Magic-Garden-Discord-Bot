import cv2
import pyautogui
from src.core import input_handler
import time
import os
import numpy as np


# Constants
IMAGE_FOLDER = "images/"


class ShopTester:
    """
    A test class for automating shop interactions using image recognition.
    """
    
    def __init__(self):
        """
        Initialize the ShopTester.
        """
        pass
    
    def open_shop(self):
        """
        Open the shop by simulating keystrokes.
        Presses Shift+1, waits, then Space to enter the shop.
        Verifies the shop is open by looking for the shop header image.
        """
        print("Opening shop...")
        print("DEBUG: Sending Shift+1 (using input_handler)...")
        
        # Press Shift+1 with explicit holds for game input detection
        input_handler.key_down('shift')
        time.sleep(0.2)
        input_handler.key_down('1')
        time.sleep(0.2)
        input_handler.key_up('1')
        input_handler.key_up('shift')
        print("DEBUG: Shift+1 sent, waiting...")
        time.sleep(0.5)
        
        # Press Space with explicit hold
        print("DEBUG: Sending Space (using input_handler)...")
        input_handler.key_down('space')
        time.sleep(0.2)
        input_handler.key_up('space')
        print("DEBUG: Space sent, waiting...")
        time.sleep(0.5)
        
        # Verify shop is open using image recognition
        print("Verifying shop is open...")
        screenshot = np.array(pyautogui.screenshot())
        screenshot = cv2.cvtColor(cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        
        # Load the template image
        template_path = os.path.join(IMAGE_FOLDER, "seed_shop_header.png")
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if template is None:
            print(f"Error: Could not load template image at {template_path}")
            exit(1)
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Check if confidence is above threshold
        if max_val >= 0.8:
            print(f"Shop opened successfully (confidence: {max_val:.2f})")
        else:
            print(f"Failed to open shop (confidence: {max_val:.2f})")
            exit(1)
    
    def find_item(self, item_image_name):
        """
        Find an item on screen by image matching.
        If not found, scroll down and retry up to 3 times.
        
        Args:
            item_image_name: Name of the image file to search for
            
        Returns:
            tuple: (x, y) coordinates of the item center if found, None otherwise
        """
        max_attempts = 3
        
        for attempt in range(max_attempts):
            print(f"Searching for {item_image_name} (attempt {attempt + 1}/{max_attempts})...")
            
            # Take screenshot and convert to grayscale
            screenshot = np.array(pyautogui.screenshot())
            screenshot_gray = cv2.cvtColor(cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            
            # Load the template image
            template_path = os.path.join(IMAGE_FOLDER, item_image_name)
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
            if template is None:
                print(f"Error: Could not load template image at {template_path}")
                return None
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Check if confidence is above threshold
            if max_val >= 0.8:
                # Calculate center coordinates
                template_height, template_width = template.shape
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                print(f"Found {item_image_name} at ({center_x}, {center_y}) with confidence {max_val:.2f}")
                return (center_x, center_y)
            else:
                print(f"Item not found (confidence: {max_val:.2f})")
                
                # If not the last attempt, scroll down and wait
                if attempt < max_attempts - 1:
                    print("Scrolling down...")
                    pyautogui.scroll(-3)  # Negative value scrolls down
                    time.sleep(1)  # Wait for animation to settle
        
        print(f"Failed to find {item_image_name} after {max_attempts} attempts")
        return None
    
    def buy_item(self, item_name_image):
        """
        Purchase an item by finding it and clicking the buy button.
        
        Args:
            item_name_image: Name of the item image file to purchase
            
        Returns:
            bool: True if purchase was successful, False otherwise
        """
        print(f"Attempting to buy item: {item_name_image}")
        
        # Find the item
        item_coords = self.find_item(item_name_image)
        
        if item_coords is None:
            print(f"Error: Could not find item {item_name_image}")
            return False
        
        # Click on the item
        print(f"Clicking on item at {item_coords}")
        pyautogui.click(item_coords[0], item_coords[1])
        time.sleep(0.5)  # Wait for UI to update
        
        # Look for the green buy button
        print("Looking for buy button...")
        screenshot = np.array(pyautogui.screenshot())
        screenshot_gray = cv2.cvtColor(cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
        
        # Load the buy button template
        buy_button_path = os.path.join(IMAGE_FOLDER, "buy_button_green.png")
        buy_button_template = cv2.imread(buy_button_path, cv2.IMREAD_GRAYSCALE)
        
        if buy_button_template is None:
            print(f"Error: Could not load buy button template at {buy_button_path}")
            return False
        
        # Perform template matching for buy button
        result = cv2.matchTemplate(screenshot_gray, buy_button_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Check if buy button is found
        if max_val >= 0.8:
            # Calculate center coordinates of buy button
            btn_height, btn_width = buy_button_template.shape
            btn_center_x = max_loc[0] + btn_width // 2
            btn_center_y = max_loc[1] + btn_height // 2
            
            print(f"Found buy button at ({btn_center_x}, {btn_center_y}), clicking...")
            pyautogui.click(btn_center_x, btn_center_y)
            print(f"Successfully purchased {item_name_image}!")
            return True
        else:
            print(f"Error: Could not find buy button (confidence: {max_val:.2f})")
            return False
    
    def close_shop(self):
        """
        Close the shop and all windows by pressing Esc twice.
        Then return to garden by pressing Shift+2.
        """
        print("Closing shop...")
        input_handler.press('esc')
        time.sleep(0.5)
        input_handler.press('esc')
        time.sleep(0.5)
        print("Shop closed.")
        
        # Return to garden
        print("Returning to garden...")
        input_handler.key_down('shift')
        time.sleep(0.2)
        input_handler.key_down('2')
        time.sleep(0.2)
        input_handler.key_up('2')
        input_handler.key_up('shift')
        time.sleep(0.5)
        print("Returned to garden.")
    
    def run(self):
        """
        Execute the full shop automation sequence.
        Opens the shop, purchases an item, and closes the shop.
        """
        print("Starting shop automation...")
        
        # Open the shop
        self.open_shop()
        
        # Purchase the item
        success = self.buy_item('text_carrot.png')
        
        if success:
            print("Purchase completed successfully!")
        else:
            print("Purchase failed!")
        
        # Close the shop
        self.close_shop()
        
        print("Shop automation completed.")


if __name__ == '__main__':
    print("Shop automation starting in...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("GO!\n")
    
    tester = ShopTester()
    tester.run()
