# chroma_vault.py - Enhanced dengan memory retrieval

import chromadb
from datetime import datetime
import os
import time
import random

class MayaVault:
    """Digital Bunker - ChromaDB memory with mood context"""
    
    def __init__(self, collection_name="maya_chats"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Kategori khas untuk memory penting
        self.important_categories = {
            'makanan': ['suka', 'makan', 'minum', 'teh', 'kopi', 'nasi', 'lauk'],
            'perasaan': ['sedih', 'gembira', 'stres', 'penat', 'rindu'],
            'kegemaran': ['suka', 'minat', 'hobi', 'gemar'],
            'janji': ['janji', 'akan', 'nanti', 'esok'],
            'first_time': ['pertama', 'first', 'pertama kali']
        }
        
    def save_to_vault(self, entry, mood_context=None):
        """Save message with mood metadata and priority"""
        
        # Tentukan kategori dan priority
        content = entry["content"].lower()
        category = self._detect_category(content)
        is_important = self._is_important(content)
        
        metadata = {
            "role": entry["role"],
            "timestamp": datetime.now().isoformat(),
            "mood": mood_context.get("mood", "unknown") if mood_context else "unknown",
            "stress_level": str(mood_context.get("stress_level", 0)) if mood_context else "0",
            "category": category,
            "priority": "high" if is_important else "normal",
            "immortal": str(is_important)  # Important memories jadi immortal
        }
        
        doc_id = f"{entry['role']}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        self.collection.add(
            documents=[entry["content"]],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        # Kalau penting, simpan jugak dalam special collection
        if is_important:
            self._save_to_important(entry, metadata)
    
    def _detect_category(self, content):
        """Detect kategori memory berdasarkan keywords"""
        for category, keywords in self.important_categories.items():
            if any(keyword in content for keyword in keywords):
                return category
        return "general"
    
    def _is_important(self, content):
        """Check kalau memory ni penting (personal preferences, janji, first time)"""
        important_indicators = [
            'suka', 'minat', 'gemar', 'janji', 
            'pertama kali', 'first time', 'rindu',
            'teh tarik', 'kopi', 'makanan'
        ]
        return any(indicator in content for indicator in important_indicators)
    
    def _save_to_important(self, entry, metadata):
        """Save to important memory collection"""
        # In real implementation, maybe separate collection
        # Untuk sekarang, kita just tag in metadata
        pass
    
    def load_from_vault(self, limit=50, context=None):
        """Load recent messages with context-aware retrieval"""
        try:
            results = self.collection.get()
            
            messages = []
            if results and results['documents']:
                # Kalau ada context, kita prioritise memory yang relevan
                if context:
                    messages = self._retrieve_with_context(results, context, limit)
                else:
                    for i, doc in enumerate(results['documents'][-limit:]):
                        metadata = results['metadatas'][i] if results['metadatas'] else {}
                        messages.append({
                            "role": metadata.get("role", "assistant"),
                            "content": doc,
                            "timestamp": metadata.get("timestamp", ""),
                            "category": metadata.get("category", "general"),
                            "priority": metadata.get("priority", "normal")
                        })
            
            return messages
        except:
            return []
    
    def _retrieve_with_context(self, results, context, limit):
        """Retrieve memory based on context (e.g., topik minuman)"""
        context_lower = context.lower()
        relevant_messages = []
        
        # Keywords untuk context yang berbeza
        context_keywords = {
            'minum': ['teh', 'kopi', 'air', 'minum', 'milo', 'nescafe'],
            'makan': ['makan', 'nasi', 'lauk', 'roti', 'mee'],
            'penat': ['penat', 'stres', 'letih', 'rehat'],
            'rindu': ['rindu', 'sayang', 'miss'],
        }
        
        # Cari keywords yang relevan dengan context
        relevant_keywords = []
        for key, keywords in context_keywords.items():
            if key in context_lower or any(k in context_lower for k in keywords):
                relevant_keywords.extend(keywords)
        
        # Loop through all messages
        for i, doc in enumerate(results['documents']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            doc_lower = doc.lower()
            
            # Check kalau message ni relevan dengan context
            score = 0
            for keyword in relevant_keywords:
                if keyword in doc_lower:
                    score += 1
            
            # Priority tinggi kalau immortal atau high priority
            if metadata.get('priority') == 'high':
                score += 3
            if metadata.get('immortal') == 'True':
                score += 5
            
            if score > 0:
                relevant_messages.append({
                    "role": metadata.get("role", "assistant"),
                    "content": doc,
                    "timestamp": metadata.get("timestamp", ""),
                    "category": metadata.get("category", "general"),
                    "priority": metadata.get("priority", "normal"),
                    "relevance_score": score
                })
        
        # Sort by relevance score (highest first) and return top 'limit'
        relevant_messages.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_messages[:limit]
    
    def get_important_memories(self, category=None):
        """Get all important memories, optionally filtered by category"""
        try:
            results = self.collection.get()
            important = []
            
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    if metadata.get('priority') == 'high' or metadata.get('immortal') == 'True':
                        if not category or metadata.get('category') == category:
                            important.append({
                                "content": doc,
                                "category": metadata.get('category'),
                                "timestamp": metadata.get('timestamp')
                            })
            return important
        except:
            return []
    
    def search_by_topic(self, topic):
        """Search memory by topic (e.g., 'minuman', 'makanan')"""
        return self._retrieve_with_context(self.collection.get(), topic, 10)