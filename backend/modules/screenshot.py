import os
import time
from supabase import create_client
from PIL import ImageGrab
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def capture_screenshot():
    img = ImageGrab.grab()
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    file_path = f"screenshots/{int(time.time())}.png"
    response = supabase.storage.from_("screenshots").upload(file_path, img_bytes, content_type="image/png")

    return response.get("Key", "")

if __name__ == "__main__":
    print(capture_screenshot())
