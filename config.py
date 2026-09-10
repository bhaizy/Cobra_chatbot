import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# Telegram API Credentials
API_ID = int(os.getenv("API_ID", "10248430"))
API_HASH = os.getenv("API_HASH", "42396a6ff14a569b9d59931643897d0d")
BOT_TOKEN = os.getenv("BOT_TOKEN", "5709229627:AAHWn-lp3r3BXK7kRs8_vnmRIQnUMHRV2bU")

# MongoDB Database URL
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://AyraMusic:Ayra@cluster0.gnakzem.mongodb.net/?retryWrites=true&w=majority"
)

# Bot Information & Customization
BOT_NAME = os.getenv("BOT_NAME", "Cobra Chatbot")
BOT_USERNAME = os.getenv("BOT_USERNAME", "CobraChatBot")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "COVIDBABA")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/+IdSOWT2mDr9hOTQ1")
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/+CN0MlYIFGsAyNGI1")

# Media / Thumbnail URL (video/animation mp4 or image)
MEDIA_URL = os.getenv(
    "MEDIA_URL",
    "https://graph.org/file/a0d949ae033c97bb60c0b-238eeecbc9c32d092f.mp4"
)
