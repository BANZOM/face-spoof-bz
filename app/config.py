import os

class Config:
    MODEL_DIR = os.getenv("MODEL_DIR", "./resources/anti_spoof_models")
    DEVICE_ID = int(os.getenv("DEVICE_ID", 0))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

config = Config()