# app.py - Main Streamlit App (Maya V3) - FIXED VERSION

import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import threading
import os

# Import modules kita
from mood_detector import MoodDetector
from mood_db import MoodDatabase
from chroma_vault import MayaVault
from config import Config
from audit_logger import AuditLogger
from proactive_engine import ProactiveIntelligence


# ========== INITIALIZATION ==========

# Page config (MESTI PALING ATAS)
st.set_page_config(
    page_title=f"MaYa Petite V3 | 🌸", 
    page_icon="🌸", 
    layout="wide"
)

# Initialize all components
config = Config()
genai.configure(api_key=config.GEMINI_API_KEY)
mood_detector = MoodDetector()
mood_db = MoodDatabase(config.SQLITE_PATH)
vault = MayaVault()
audit_logger = AuditLogger()
proactive_engine = ProactiveIntelligence()

# ========== SESSION STATE ==========

if "messages" not in st.session_state:
    st.session_state.messages = vault.load_from_vault()

# Mood tracking
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "Lembut"
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []
if "mood_locked" not in st.session_state:
    st.session_state.mood_locked = False
if "suggested_mood" not in st.session_state:
    st.session_state.suggested_mood = None
if "mood_notification" not in st.session_state:
    st.session_state.mood_notification = None

# Stats
if "interaction_count" not in st.session_state:
    st.session_state.interaction_count = 0
if "auto_switch_count" not in st.session_state:
    st.session_state.auto_switch_count = 0

# ========== HELPER FUNCTIONS ==========

def generate_greeting():
    """Maya generate greeting sendiri based on context"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        waktu = "pagi"
    elif 12 <= hour < 14:
        waktu = "tengah hari"
    elif 14 <= hour < 18:
        waktu = "petang"
    elif 18 <= hour < 20:
        waktu = "maghrib"
    else:
        waktu = "malam"
    
    prompt = f"""Sekarang waktu {waktu}. 
    Kau adalah MaYa, personal assistant untuk Abang.
    Mood kau sekarang: {st.session_state.current_mood}
    
    Tulis SATU ayat greeting yang natural untuk Abang.
    Guna bahasa Melayu campur English sikit (Manglish).
    Jangan panjang sangat. Terus tulis ayat je.
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        fallback = {
            "pagi": "Selamat pagi Abang! ☀️ Ada apa-apa yang dinda boleh tolong?",
            "tengah hari": "Selamat tengah hari Abang! Dah lunch? 🍜",
            "petang": "Selamat petang Abang. Minum petang dulu? ☕",
            "maghrib": "Abang, dah maghrib ni. Jangan lupa rehat jap 🌙",
            "malam": "Selamat malam Abang. Masih bertenaga? Dinda teman ✨"
        }
        return fallback.get(waktu, "Hai Abang! Apa khabar? 🌸")

def background_mood_scan(user_input):
    """Background mood detection - guna file instead of session_state"""
    import json
    import os
    import time
    
    current_mood = "Lembut"
    mood_locked = False
    
    if os.path.exists('temp_state.json'):
        try:
            with open('temp_state.json', 'r') as f:
                state = json.load(f)
                current_mood = state.get('current_mood', 'Lembut')
                mood_locked = state.get('mood_locked', False)
        except:
            pass
    
    if mood_locked:
        return
    
    result = mood_detector.detect(user_input)
    
    if (result['mood'] and 
        result['confidence'] >= 0.6 and
        result['mood'] != current_mood):
        
        suggestion = {
            'mood': result['mood'],
            'confidence': result['confidence'],
            'reason': result['reason'],
            'timestamp': time.time()
        }
        
        with open('temp_mood_suggestion.json', 'w') as f:
            json.dump(suggestion, f)

def read_mood_suggestion():
    """Baca mood suggestion dari file (panggil dalam main thread)"""
    import json
    import os
    import time
    
    try:
        if os.path.exists('temp_mood_suggestion.json'):
            with open('temp_mood_suggestion.json', 'r') as f:
                data = json.load(f)
            
            if time.time() - data['timestamp'] < 5:
                st.session_state.suggested_mood = data
            
            os.remove('temp_mood_suggestion.json')
    except:
        pass

def apply_suggested_mood():
    """Apply suggested mood"""
    if st.session_state.suggested_mood and not st.session_state.mood_locked:
        suggestion = st.session_state.suggested_mood
        
        mood_db.log_mood_switch(
            from_mood=st.session_state.current_mood,
            to_mood=suggestion['mood'],
            reason=suggestion['reason'],
            confidence=suggestion['confidence'],
            trigger_type="auto",
            user_message="[background detection]"
        )
        
        st.session_state.mood_history.append({
            "from": st.session_state.current_mood,
            "to": suggestion['mood'],
            "time": datetime.now().strftime("%H:%M"),
            "reason": suggestion['reason'],
            "type": "auto"
        })
        
        st.session_state.current_mood = suggestion['mood']
        st.session_state.auto_switch_count += 1
        
        if suggestion['mood'] == "Lembut":
            st.session_state.mood_notification = "🌸 Dinda perasan Abang macam penat. Dinda switch ke mode Lembut."
        elif suggestion['mood'] == "Bijak":
            st.session_state.mood_notification = "🧠 Dinda switch ke mode Bijak. Jom kita analisis data."
        elif suggestion['mood'] == "Tegas":
            st.session_state.mood_notification = "⚡ Mode Tegas activated."
        
        st.session_state.suggested_mood = None

# ========== UI SETUP ==========

st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; color: #FFFFFF; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; 
                     border: 1px solid #444; background-color: #1E1E1E; }
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #FFFFFF !important; font-size: 1.05rem; }
    .stButton>button { background-color: #D4AF37; color: black; 
                       border-radius: 20px; font-weight: bold; width: 100%; }
    h1, h2, h3, h4 { color: #D4AF37 !important; }
    [data-testid="stSidebar"] { color: #FFFFFF; }
    .mood-badge { background-color: #D4AF37; color: #0A0A0A; padding: 5px 10px;
                  border-radius: 20px; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========

with st.sidebar:
    st.title("🌸 MaYa Petite V3")
    st.markdown(f"*Personal AI untuk {config.MASTER_NAME}*")
    st.markdown("---")
    
    mood_icons = {"Tegas": "⚡", "Bijak": "🧠", "Lembut": "🌸", "Memujuk": "🤝"}
    
    st.markdown("### 🎭 Manual Mood Control")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_mood = st.select_slider(
            "Pilih mood:",
            options=["Tegas", "Bijak", "Lembut", "Memujuk"],
            value=st.session_state.current_mood,
            key="manual_mood",
            disabled=st.session_state.mood_locked
        )
    with col2:
        st.markdown(f"# {mood_icons[selected_mood]}")
    
    if not st.session_state.mood_locked and selected_mood != st.session_state.current_mood:
        mood_db.log_mood_switch(
            from_mood=st.session_state.current_mood,
            to_mood=selected_mood,
            reason="manual_selection",
            confidence=1.0,
            trigger_type="manual"
        )
        st.session_state.current_mood = selected_mood
        st.session_state.mood_history.append({
            "from": st.session_state.current_mood,
            "to": selected_mood,
            "time": datetime.now().strftime("%H:%M"),
            "reason": "manual",
            "type": "manual"
        })
    
    lock_col1, lock_col2 = st.columns([1, 3])
    with lock_col1:
        lock_status = st.checkbox("🔒", value=st.session_state.mood_locked)
    with lock_col2:
        st.markdown("**Lock Mood**")
    
    if lock_status != st.session_state.mood_locked:
        st.session_state.mood_locked = lock_status
    
    st.markdown("---")
    
    with st.expander("🤖 Auto Mood Detection"):
        st.caption(f"Auto-switches today: {st.session_state.auto_switch_count}")
        
        if st.session_state.suggested_mood:
            sug = st.session_state.suggested_mood
            st.info(f"Suggested: {sug['mood']} ({sug['confidence']:.0%})")
            if st.button("Apply Now"):
                apply_suggested_mood()
                st.rerun()
    
    with st.expander("📜 Mood History"):
        for entry in st.session_state.mood_history[-5:]:
            icon = mood_icons.get(entry['to'], '🌸')
            st.caption(f"{entry['time']}: {entry['from']} → {entry['to']} {icon}")
    
    st.markdown(f"""
    <div class="mood-badge">
        Current: {st.session_state.current_mood} {mood_icons[st.session_state.current_mood]}
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.mood_notification:
        st.success(st.session_state.mood_notification)
        if st.button("Dismiss"):
            st.session_state.mood_notification = None
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📎 Upload PDF", type="pdf")
    if uploaded_file:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc_text = ""
        for page in pdf_reader.pages:
            doc_text += page.extract_text()
        st.session_state.context_document = doc_text
        st.success("✅ Dokumen diproses")
    
    if st.button("🔄 Reset Session"):
        st.session_state.messages = []
        if "greeted" in st.session_state:
            del st.session_state.greeted
        st.rerun()

# ========== MAIN CHAT UI ==========

st.title("💬 Chat dengan MaYa")
st.caption(f"Mood sekarang: {st.session_state.current_mood} {mood_icons[st.session_state.current_mood]}")

# Display greeting if new session
if "greeted" not in st.session_state:
    with st.chat_message("assistant"):
        greeting = generate_greeting()
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.greeted = True

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== PROACTIVE MESSAGE ==========

# Cuba dapatkan proactive message berdasarkan masa
proactive_msg = proactive_engine.get_proactive_message()

if proactive_msg:
    # Double-check messages ada
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Tampil proactive message
    with st.chat_message("assistant"):
        st.markdown(proactive_msg)
    st.session_state.messages.append({"role": "assistant", "content": proactive_msg})

# ========== CHAT INPUT & RESPONSE ==========

if prompt := st.chat_input("Apa yang Abang nak sembang hari ni?"):
    
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Save user message
    user_entry = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_entry)
    vault.save_to_vault(user_entry)
    # SELEPAS user_entry disimpan
    # Retrieve relevant memories based on user input
    relevant_memories = vault.search_by_topic(prompt)
    if relevant_memories:
        # Tambah dalam context untuk Maya
        memory_context = "\n\n[KENANGAN BERKAITAN]:\n"
        for mem in relevant_memories[:3]:  # Ambil 3 paling relevan
            memory_context += f"- Abang pernah cakap: '{mem['content']}'\n"
    
        # Akan digunakan dalam prompt ke Gemini
        st.session_state.memory_context = memory_context
    else:
        st.session_state.memory_context = ""
    
    
    # 3. Trigger background mood scan
    threading.Thread(target=background_mood_scan, args=(prompt,)).start()
    
    # 4. Get Maya's response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        start_time = time.time()
        
        try:
            mood_prompt = mood_detector.get_mood_prompt(st.session_state.current_mood)
            
            doc_context = st.session_state.get("context_document", "")
            if doc_context:
                mood_prompt += f"\n\n[CONTEXT]: {doc_context[:2000]}"
            
            # FIXED: Cara baru hantar instruction
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            full_prompt = f"{mood_prompt}\n\n{st.session_state.get('memory_context', '')}\nUser: {prompt}\n\nMaya:"            
            response = model.generate_content(full_prompt)
            full_response = response.text
            
            response_placeholder.markdown(full_response)
            
            # Save assistant response
            assistant_entry = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(assistant_entry)
            vault.save_to_vault(assistant_entry)
            
            # 5. Check for mood suggestion
            read_mood_suggestion()
            
            if st.session_state.suggested_mood and not st.session_state.mood_locked:
                apply_suggested_mood()
                if st.session_state.mood_notification:
                    st.caption(st.session_state.mood_notification)
                    st.session_state.mood_notification = None
            
        except Exception as e:
            st.error(f"Error: {e}")
            assistant_entry = {"role": "assistant", "content": f"Error: {e}"}
            st.session_state.messages.append(assistant_entry)

# ========== AUTO-SAVE ON EXIT ==========
import atexit

def save_on_exit():
    mood_db.update_daily_summary(
        dominant_mood=st.session_state.current_mood,
        stress_level=0.5,
        focus_level=0.5,
        message_count=len(st.session_state.messages)
    )
    mood_db.log_audit_event("session_end", {
        "messages": len(st.session_state.messages),
        "final_mood": st.session_state.current_mood
    })

atexit.register(save_on_exit)