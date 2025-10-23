import os

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Model Configuration
MOONDREAM_API_URL = os.getenv("MOONDREAM_API_URL", "http://localhost:2020")
MOONDREAM_QUERY_ENDPOINT = f"{MOONDREAM_API_URL}/v1/query"

# Storage Configuration
IMAGES_DIR = os.getenv("IMAGES_DIR", "data/images")
VIDEO_DIR = os.getenv("VIDEO_DIR", "data/videos")
LOGS_DIR = os.getenv("LOGS_DIR", "data/logs")

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# API Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".mp4", ".avi", ".mov"]

# Scenario Configuration
SUPPORTED_SCENARIOS = [
    "smoke_detection",
    "fire_detection", 
    "fall_detection",
    "debris_detection",
    "missing_fire_extinguisher",
    "unattended_object"
]
