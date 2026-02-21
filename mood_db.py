# memory/mood_db.py

import sqlite3
from datetime import datetime
import json
import os

class MoodDatabase:
    """SQLite database untuk track mood history & audit log"""
    
    def __init__(self, db_path="maya_mood.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if not exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Mood switches log
        c.execute('''
            CREATE TABLE IF NOT EXISTS mood_switches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                from_mood TEXT,
                to_mood TEXT,
                reason TEXT,
                confidence REAL,
                trigger_type TEXT,
                user_message TEXT
            )
        ''')
        
        # Daily mood summary
        c.execute('''
            CREATE TABLE IF NOT EXISTS mood_summary (
                date TEXT PRIMARY KEY,
                dominant_mood TEXT,
                stress_level REAL,
                focus_level REAL,
                message_count INTEGER,
                summary TEXT
            )
        ''')
        
        # Audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_mood_switch(self, from_mood, to_mood, reason, confidence, trigger_type, user_message=""):
        """Record setiap kali mood bertukar"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO mood_switches 
            (timestamp, from_mood, to_mood, reason, confidence, trigger_type, user_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            from_mood,
            to_mood,
            reason,
            confidence,
            trigger_type,
            user_message[:200]  # limit panjang
        ))
        conn.commit()
        conn.close()
    
    def get_today_summary(self):
        """Dapatkan summary mood untuk hari ni"""
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM mood_summary WHERE date = ?', (today,))
        result = c.fetchone()
        conn.close()
        return result
    
    def update_daily_summary(self, dominant_mood, stress_level, focus_level, message_count):
        """Update atau create daily summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if exists
        c.execute('SELECT date FROM mood_summary WHERE date = ?', (today,))
        if c.fetchone():
            c.execute('''
                UPDATE mood_summary 
                SET dominant_mood = ?, stress_level = ?, focus_level = ?, message_count = ?
                WHERE date = ?
            ''', (dominant_mood, stress_level, focus_level, message_count, today))
        else:
            c.execute('''
                INSERT INTO mood_summary (date, dominant_mood, stress_level, focus_level, message_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (today, dominant_mood, stress_level, focus_level, message_count))
        
        conn.commit()
        conn.close()
    
    def get_audit_data(self, days=7):
        """Ambil data untuk audit (last X days)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get mood switches for last X days
        c.execute('''
            SELECT * FROM mood_switches 
            WHERE datetime(timestamp) > datetime('now', ?)
            ORDER BY timestamp DESC
        ''', (f'-{days} days',))
        switches = c.fetchall()
        
        # Get daily summaries
        c.execute('''
            SELECT * FROM mood_summary 
            WHERE date > date('now', ?)
            ORDER BY date DESC
        ''', (f'-{days} days',))
        summaries = c.fetchall()
        
        conn.close()
        return {'switches': switches, 'summaries': summaries}
    
    def log_audit_event(self, event_type, details):
        """Log event untuk audit trail"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO audit_log (timestamp, event_type, details)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), event_type, json.dumps(details)))
        conn.commit()
        conn.close()