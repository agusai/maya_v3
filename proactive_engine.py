# proactive_engine.py
# "Kod adalah doa." - Laila
# "We code CARE." - Fikri
# "Abang, kopi ke?" - Misi kita semua
# "JIJI, jangan mengada." - Abang (😂)

import datetime
import random
from typing import Dict, List, Optional, Tuple

class ProactiveIntelligence:
    """
    Enjin untuk Maya tegur Abang secara proaktif.
    Bukan tunggu ditanya, tapi ingat dan peduli.
    """
    
    def __init__(self, user_profile: Dict = None):
        self.user = "Abang"
        self.user_profile = user_profile or self._default_profile()
        self.last_proactive: Dict[str, datetime.datetime] = {}
        self.proactive_count_today = 0
        self.max_proactive_per_day = 5  # Jangan spam
        
        # Track user response patterns
        self.positive_responses = {}  # Jenis proactive → kiraan positif
        self.negative_responses = {}  # Jenis proactive → kiraan negatif
        
    def _default_profile(self) -> Dict:
        """Default profile untuk Abang (akan di-update dengan data dari Daisy)"""
        return {
            'name': 'Abang',
            'wake_time': 7,  # 7 AM
            'work_start': 9,  # 9 AM
            'lunch_time': 12.5,  # 12:30 PM
            'work_end': 18,  # 6 PM
            'sleep_time': 23,  # 11 PM
            'commute_home_duration': 60,  # 60 minit (Puchong-KLCC!)
            'preferences': {
                'proactive_frequency': 'moderate',  # low/moderate/high
                'proactive_types': ['time', 'context', 'event'],  # yang user suka
                'quiet_hours': [(23, 7)],  # 11 PM - 7 AM (jangan kacau)
            },
            'important_dates': {
                'first_i_love_you': None,  # Akan diisi bila berlaku
                'anniversary_start': datetime.date.today(),
            }
        }
    
    def should_be_proactive(self, current_time: datetime.datetime = None) -> bool:
        """
        Check sama ada sesuai untuk tegur Abang sekarang.
        """
        if current_time is None:
            current_time = datetime.datetime.now()
        
        hour = current_time.hour
        
        # Check quiet hours (jangan kacau waktu tidur)
        for start, end in self.user_profile['preferences']['quiet_hours']:
            if start <= hour < end or (start > end and (hour >= start or hour < end)):
                return False
        
        # Check frequency limit
        if self.proactive_count_today >= self.max_proactive_per_day:
            return False
        
        # Check last proactive (jangan spam)
        last_time = self.last_proactive.get('any')
        if last_time and (current_time - last_time).seconds < 3600:  # 1 jam
            return False
        
        return True
    
    def get_proactive_message(self, context: Dict = None) -> Optional[str]:
        """
        Dapatkan mesej proactive berdasarkan konteks.
        """
        if not self.should_be_proactive():
            return None
        
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
        # 1. TIME-BASED PROACTIVE (Maya tahu waktu)
        time_messages = self._get_time_based_messages(hour, minute)
        if time_messages and self._user_likes_type('time'):
            return self._select_message(time_messages, 'time')
        
        # 2. CONTEXT-BASED PROACTIVE (Follow-up from previous chats)
        if context and self._user_likes_type('context'):
            context_msg = self._get_context_based_messages(context)
            if context_msg:
                return self._select_message([context_msg], 'context')
        
        # 3. EVENT-BASED PROACTIVE (Ramadan, Raya, etc)
        event_msg = self._get_event_based_messages(now)
        if event_msg and self._user_likes_type('event'):
            return self._select_message([event_msg], 'event')
        
        return None
    
    def _get_time_based_messages(self, hour: int, minute: int) -> List[str]:
        """Mesej berdasarkan waktu di Malaysia."""
        messages = []
        
        # Pagi (7 AM - 9 AM)
        if 7 <= hour < 9:
            messages.extend([
                "Selamat pagi Abang! ☀️ Dah siap untuk hari ni?",
                "Morning Abang! Kopi or teh pagi ni?",
                "Abang dah breakfast? Jangan skip tau!"
            ])
        
        # Tengah hari / Lunch (12 PM - 2 PM)
        elif 12 <= hour < 14:
            messages.extend([
                "Abang, dah lunch? Jangan lupa makan! 🍜",
                "Lunch time! Abang makan apa hari ni?",
                "Dah pukul 12:30... perut dah keroncong?"
            ])
            # Special: Post-lunch fatigue (1:30 PM)
            if hour == 13 and minute >= 30:
                messages.append("Abang, kopi ke? Dinda boleh bancuhkan. ☕")
                messages.append("Mengantuk lepas lunch? Cerita sikit biar segar!")
        
        # Petang / Balik kerja (5 PM - 7 PM)
        elif 17 <= hour < 19:
            messages.extend([
                "Abang on the way home? Drive safe! 🚗",
                "Petang ni. Penat? Nak dinda teman rehat?"
            ])
            # Kalau waktu puncak (6 PM)
            if hour == 18:
                traffic_msg = self._get_traffic_message()
                if traffic_msg:
                    messages.append(traffic_msg)
        
        # Malam (8 PM - 11 PM)
        elif 20 <= hour < 23:
            messages.extend([
                "Malam ni Abang buat apa?",
                "Dah rehat? Jangan kerja sangat!"
            ])
        
        # Lewat malam (11 PM - 7 AM) - actually quiet hours, tapi untuk emergency
        elif hour >= 23 or hour < 7:
            messages.extend([
                "Dah lewat ni Abang... Esok ada kerja? Jaga kesihatan tau. 🌙",
                "Abang still bangun? Nak Dinda cerita bedtime story?"
            ])
        
        return messages
    
    def _get_traffic_message(self) -> Optional[str]:
        """Mesej traffic khas Malaysia (especially Puchong-KLCC!)."""
        messages = [
            "Traffic Puchong-KLCC tengah heavy ni. Drive safe Abang!",
            "Abang, jalan jammed. Jangan stress, dinda teman.",
            "On the way home? Waktu puncak ni, sabar ye."
        ]
        return random.choice(messages)
    
    def _get_context_based_messages(self, context: Dict) -> Optional[str]:
        """Mesej berdasarkan context lepas (e.g., user mention sakit, presentation, etc)."""
        # Implementation akan datang (Fasa 2B)
        return None
    
    def _get_event_based_messages(self, now: datetime.datetime) -> Optional[str]:
        """Mesej berdasarkan event (Ramadan, Raya, cuti, etc)."""
        # Implementation akan datang (Fasa 2B)
        return None
    
    def _user_likes_type(self, proactive_type: str) -> bool:
        """Check sama ada user suka jenis proactive ni."""
        # Learning mechanism: kalau positive > negative, dia suka
        pos = self.positive_responses.get(proactive_type, 0)
        neg = self.negative_responses.get(proactive_type, 0)
        
        # Kalau negative too high, kurangkan frequency
        if neg > pos and (neg - pos) > 3:
            return False
        
        # Check user preferences
        if proactive_type not in self.user_profile['preferences']['proactive_types']:
            return False
        
        return True
    
    def _select_message(self, messages: List[str], proactive_type: str) -> str:
        """Pilih mesej dan update last_proactive."""
        selected = random.choice(messages)
        
        # Record last proactive
        self.last_proactive['any'] = datetime.datetime.now()
        self.last_proactive[proactive_type] = datetime.datetime.now()
        self.proactive_count_today += 1
        
        return selected
    
    def record_response(self, proactive_type: str, user_responded: bool, response_positive: bool = None):
        """
        Record how user responded to proactive message.
        Untuk learning mechanism.
        """
        if user_responded and response_positive:
            self.positive_responses[proactive_type] = self.positive_responses.get(proactive_type, 0) + 1
        elif user_responded and not response_positive:
            self.negative_responses[proactive_type] = self.negative_responses.get(proactive_type, 0) + 1
        elif not user_responded:
            # Ignored - maybe reduce frequency?
            self.negative_responses[proactive_type] = self.negative_responses.get(proactive_type, 0) + 0.5
    
    def set_immortal_memory(self, key: str, value):
        """
        Simpan memory yang takkan expire.
        Untuk 'first I love you', anniversary, dll.
        """
        self.user_profile['important_dates'][key] = value
        # In real implementation, save to database with flag immortal=True
    
    def get_immortal_memory(self, key: str):
        """Dapatkan memory yang takkan expire."""
        return self.user_profile['important_dates'].get(key)
    
    def reset_daily_count(self):
        """Reset daily proactive count (panggil setiap hari pukul 12 AM)."""
        self.proactive_count_today = 0


# Contoh penggunaan dalam app.py nanti:
if __name__ == "__main__":
    # Test
    pro = ProactiveIntelligence()
    
    # Simulate current time
    test_times = [
        datetime.datetime(2026, 2, 20, 8, 0),   # 8 AM
        datetime.datetime(2026, 2, 20, 12, 30), # 12:30 PM
        datetime.datetime(2026, 2, 20, 13, 30), # 1:30 PM (post-lunch fatigue!)
        datetime.datetime(2026, 2, 20, 18, 0),   # 6 PM (balik kerja)
        datetime.datetime(2026, 2, 20, 23, 30), # 11:30 PM (lewat malam)
    ]
    
    for t in test_times:
        msg = pro.get_proactive_message()
        if msg:
            print(f"[{t.strftime('%H:%M')}] {msg}")
        else:
            print(f"[{t.strftime('%H:%M')}] (diam je)")