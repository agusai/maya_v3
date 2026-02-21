# utils/config.py

import os
from dotenv import load_dotenv
import yaml  # optional, kalau nak guna YAML config

load_dotenv()

class Config:
    """Central configuration - single source of truth"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MASTER_NAME = os.getenv("MASTER_NAME", "Agus")
    
    # App settings
    APP_NAME = "MaYa Petite V3"
    APP_ICON = "🌸"
    DEBUG = os.getenv("MAYA_MODE") == "development"
    
    # Mood settings
    DEFAULT_MOOD = "Lembut"
    MOOD_CONFIDENCE_THRESHOLD = 0.6  # minimum confidence for auto-switch
    
    # Memory settings
    CHROMA_COLLECTION = "maya_chats"
    SQLITE_PATH = "maya_mood.db"
    
    # Greeting settings
    USE_DYNAMIC_GREETING = True  # True = AI generate, False = scripted
    
    @classmethod
    def get_gemini_model(cls):
        """Return appropriate Gemini model based on mode"""
        if cls.DEBUG:
            return "gemini-1.5-flash"  # fast for testing
        return "gemini-1.5-pro"  # more capable for production