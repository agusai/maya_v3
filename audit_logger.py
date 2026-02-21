# core/audit_logger.py

from datetime import datetime
import json
import os

class AuditLogger:
    """Log semua interaksi untuk audit purposes"""
    
    def __init__(self, log_dir="audit_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Today's log file
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = f"{log_dir}/{today}.jsonl"
    
    def log_interaction(self, user_msg, maya_response, mood_data, response_time_ms):
        """Log satu interaction"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_msg,
            "maya_response": maya_response[:500],  # limit for file size
            "mood": mood_data.get("mood"),
            "mood_confidence": mood_data.get("confidence"),
            "mood_reason": mood_data.get("reason"),
            "response_time_ms": response_time_ms,
            "auto_switched": mood_data.get("auto_switched", False)
        }
        
        # Append to today's log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_recent_logs(self, hours=24):
        """Ambil logs untuk review"""
        # Implementation for reading logs
        pass