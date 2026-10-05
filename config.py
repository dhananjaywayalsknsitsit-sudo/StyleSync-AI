import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-before-deployment")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.getenv("MONGO_DB", "stylesync_ai")
    FASHN_API_KEY = os.getenv("FASHN_API_KEY", "")
    UPLOAD_FOLDER = str(BASE_DIR / "static" / "uploads")
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
