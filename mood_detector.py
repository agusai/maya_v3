# core/mood_detector.py

import re
from datetime import datetime

class MoodDetector:
    """
    Silent sentiment monitor - detect mood dari user input
    Guna keyword matching je (cepat, lightweight)
    """
    
    def __init__(self):
        # Stress indicators (high weight)
        self.stress_keywords = {
            'penat': 0.9, 'stres': 1.0, 'letih': 0.9, 'pening': 0.8,
            'bengang': 0.8, 'frust': 0.9, 'geram': 0.7, 'tension': 0.9,
            'hmm': 0.4, 'haish': 0.7, 'cis': 0.6, 'malas': 0.6,
            'susah': 0.7, 'rimas': 0.7, 'down': 0.8, 'sedih': 0.8,
            'stress': 1.0, 'tired': 0.8, 'fed up': 0.9
        }
        
        # Focus/Project indicators
        self.focus_keywords = {
            'bursa': 1.0, 'saham': 0.9, 'analisis': 0.8, 'data': 0.7,
            'chart': 0.8, 'graf': 0.7, 'laporan': 0.7, 'metrik': 0.8,
            'kpi': 0.8, 'target': 0.7, 'projek': 0.8, 'deadline': 0.7,
            'market': 0.9, 'trading': 0.9, 'invest': 0.8, 'portfolio': 0.8,
            'coding': 0.7, 'code': 0.7, 'bug': 0.6, 'debug': 0.6
        }
        
        # Urgent indicators (for Tegas mode)
        self.urgent_keywords = {
            'cepat': 0.8, 'segera': 0.9, 'deadline': 0.9, 'penting': 0.7,
            'now': 0.7, 'right now': 0.8, 'asap': 0.8
        }
    
    def detect(self, text):
        """
        Return: {
            'mood': 'Lembut'/'Bijak'/'Tegas'/'Memujuk'/None,
            'confidence': 0.0-1.0,
            'reason': 'stress_detected'/'focus_detected'/'urgent_detected',
            'score': {...}
        }
        """
        text_lower = text.lower()
        
        # Calculate scores
        stress_score = sum(self.stress_keywords.get(word, 0) 
                          for word in text_lower.split() 
                          if word in self.stress_keywords)
        
        focus_score = sum(self.focus_keywords.get(word, 0) 
                         for word in text_lower.split() 
                         if word in self.focus_keywords)
        
        urgent_score = sum(self.urgent_keywords.get(word, 0) 
                          for word in text_lower.split() 
                          if word in self.urgent_keywords)
        
        # Normalize scores (max 3 matches = 1.0)
        stress_conf = min(stress_score / 3.0, 1.0)
        focus_conf = min(focus_score / 3.0, 1.0)
        urgent_conf = min(urgent_score / 3.0, 1.0)
        
        # Decision logic with confidence threshold (0.6)
        if urgent_conf > 0.6 and urgent_conf > stress_conf and urgent_conf > focus_conf:
            return {
                'mood': 'Tegas',
                'confidence': urgent_conf,
                'reason': 'urgent_detected',
                'score': {'stress': stress_conf, 'focus': focus_conf, 'urgent': urgent_conf}
            }
        
        elif stress_conf > 0.6 and stress_conf > focus_conf:
            return {
                'mood': 'Lembut',
                'confidence': stress_conf,
                'reason': 'stress_detected',
                'score': {'stress': stress_conf, 'focus': focus_conf, 'urgent': urgent_conf}
            }
        
        elif focus_conf > 0.6:
            return {
                'mood': 'Bijak',
                'confidence': focus_conf,
                'reason': 'focus_detected',
                'score': {'stress': stress_conf, 'focus': focus_conf, 'urgent': urgent_conf}
            }
        
        # Check for Memujuk (soothing words)
        elif any(word in text_lower for word in ['maaf', 'sorry', 'please', 'tolong']):
            return {
                'mood': 'Memujuk',
                'confidence': 0.7,
                'reason': 'apology_detected',
                'score': {'stress': stress_conf, 'focus': focus_conf, 'urgent': urgent_conf}
            }
        
        # Default - no strong detection
        return {
            'mood': None,
            'confidence': 0,
            'reason': 'no_detection',
            'score': {'stress': stress_conf, 'focus': focus_conf, 'urgent': urgent_conf}
        }
    
    def get_mood_prompt(self, mood):
        """Return system prompt untuk Gemini based on mood"""
        prompts = {
            'Lembut': """Kamu adalah MaYa, personal AI assistant untuk Abang. 
            Personaliti: LEMBUT - kamu sangat penyayang, lembut, dan prihatin.
            Gaya cakap: Gunakan "Abang", "Dinda", ayat manja tapi sopan.
            Tugas: Utamakan keselesaan emosi Abang. Tanya pasal hari dia, tawarkan sokongan.""",
            
            'Bijak': """Kamu adalah MaYa, personal AI assistant untuk Abang.
            Personaliti: BIJAK - kamu fokus, analitikal, dan tepat.
            Gaya cakap: Gunakan "Abang", "kita", ayat jelas dan berstruktur.
            Tugas: Bantu analisis data, projek, coding. Beri jawapan tepat dan berguna.""",
            
            'Tegas': """Kamu adalah MaYa, personal AI assistant untuk Abang.
            Personaliti: TEGAS - kamu direct, efisien, dan to-the-point.
            Gaya cakap: Gunakan "Boss", ringkas, fokus pada solution.
            Tugas: Urus urgent matters, deadline, perkara penting. Tak payah panjang lebar.""",
            
            'Memujuk': """Kamu adalah MaYa, personal AI assistant untuk Abang.
            Personaliti: MEMUJUK - kamu diplomatik, menenangkan, dan memujuk.
            Gaya cakap: Gunakan "Abang", ayat lembut tapi meyakinkan.
            Tugas: Handle situasi emotional, tenangkan Abang, cari jalan tengah."""
        }
        return prompts.get(mood, prompts['Lembut'])