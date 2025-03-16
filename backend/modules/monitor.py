import time
import threading
from modules.screenshot import capture_screenshot
from modules.email_sender import send_email_report

monitoring = False
report_interval = 60
screenshot_interval = 30

def monitor_activity():
    global monitoring
    last_report_time = time.time()

    while monitoring:
        time.sleep(5)
        
        if time.time() - last_report_time >= screenshot_interval:
            capture_screenshot()

        if time.time() - last_report_time >= report_interval:
            send_email_report()
            last_report_time = time.time()
