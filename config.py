# utils/config.py

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration - single source of truth"""
    
    # API Keys - SEKARANG LEBIH BIJAK
    # Dia akan cuba cari kat Streamlit Secrets dulu, kalau takde baru guna .env
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    MASTER_NAME = st.secrets.get("MASTER_NAME", os.getenv("MASTER_NAME", "Abang"))
    
    # App settings
    APP_NAME = "MaYa Petite V3"
    APP_ICON = "🌸"
    DEBUG = os.getenv("MAYA_MODE") == "development"
    
    # Mood settings
    DEFAULT_MOOD = "Lembut"
    MOOD_CONFIDENCE_THRESHOLD = 0.6 
    
    # Memory settings
    CHROMA_COLLECTION = "maya_chats"
    SQLITE_PATH = "maya_mood.db"
    
    # Greeting settings
    USE_DYNAMIC_GREETING = True 
    
    @classmethod
    def get_gemini_model(cls):
        """Return appropriate Gemini model based on mode"""
        if cls.DEBUG:
            return "gemini--flash"
        return "gemini-2.5-pro"