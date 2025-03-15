from PIL import ImageGrab
import os
import time
import db

def capture_screenshot():
    """Capture a screenshot and store it in the database."""
    try:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_path = f"logs/screenshots/screenshot_{timestamp}.png"
        os.makedirs("logs/screenshots", exist_ok=True)
        
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)

        # Store in database
        db.store_screenshot(screenshot_path)

    except Exception as e:
        print(f"Error capturing screenshot: {e}")
