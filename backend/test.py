# import psycopg2
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Connect to Supabase PostgreSQL
# try:
#     conn = psycopg2.connect(
#         dbname=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASS"),
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT")
#     )
#     print("✅ Connected to Supabase PostgreSQL!")
#     conn.close()
# except Exception as e:
#     print("❌ Connection failed:", e)


import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()  # Load environment variables

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_RECEIVER = os.getenv("RECIEVER_EMAIL")

def send_email():
    try:
        msg = EmailMessage()
        msg.set_content("This is a test email with an attachment")
        msg["Subject"] = "Test Email"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        # Connect to SMTP Server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection

        # Login
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        # Send Email
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

send_email()


