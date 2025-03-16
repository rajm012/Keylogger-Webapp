import time
import pyautogui

def capture_screenshot():
    screenshot_path = f"./logs/screenshots/screenshot_{int(time.time())}.png"
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path
