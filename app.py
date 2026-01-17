import streamlit as st
import pandas as pd
import os
import random

# --- INITIALISIERUNG ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100
if 'order' not in st.session_state: st.session_state.order = []

# --- SIDEBAR & DESIGN ---
st.sidebar.title("🎨 Design & Logik")
shuffle = st.sidebar.checkbox("Zufällige Reihenfolge")
st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)

themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme", list(themes.keys()))
t = themes[selected_theme]
scale = st.session_state.font_scale / 100.0

# --- CSS: FIXED NAVIGATION & SCALING ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    [data-testid="stAppViewBlockContainer"] {{ padding-top: 1.5rem !important; padding-bottom: 6rem !important; }}

    .card {{ 
        padding: {25 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.3 * scale}rem; margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}

    .stButton > button {{
        width: 100% !important; border-radius: 12px !important;
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important;
        height: 3.5em !important;
        margin-bottom: 5px !important;
    }}
    .stMarkdown, p, span, label {{ color: {t['text']} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- INHALT ---
BASE_DIR = "Quizzes"
if os.path.exists(BASE_DIR):
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    cat = st.sidebar.selectbox("Kategorie", categories)
    if cat:
        path = os.path.join(BASE_DIR, cat)
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        quiz_file = st.sidebar.selectbox("Quiz", files)
        
        if quiz_file:
            df = pd.read_csv(os.path.join(path, quiz_file))
            
            if not st.session_state.order or len(st.session_state.order) != len(df):
                st.session_state.order = list(range(len(df)))
                if shuffle: random.shuffle(st.session_state.order)
            
            current_row = st.session_state.order[st.session_state.idx]
            st.progress((st.session_state.idx + 1) / len(df))

            # 1. NAVIGATION OBEN
            if st.button("Weiter ➡️"):
                st.session_state.idx = (st.session_state.idx + 1) % len(df)
                st.session_state.reveal = False
                st.rerun()

            # 2. FRAGE
            q = df.iloc[current_row, 0]
            a = df.iloc[current_row, 1]
            st.markdown(f'<div class="card">{q}</div>', unsafe_allow_html=True)
            
            # 3. ANTWORT
            if st.button("Antwort prüfen"):
                st.session_state.reveal = not st.session_state.reveal
            if st.session_state.reveal:
                st.info(f"**Antwort:** {a}")
                
            # 4. NAVIGATION UNTEN
            st.write("---") 
            if st.button("⬅️ Zurück (1 Karte)"):
                st.session_state.idx = (st.session_state.idx - 1) % len(df)
                st.session_state.reveal = False
                st.rerun()
            
            if st.button("⏪ 10 Karten zurück"):
                st.session_state.idx = (st.session_state.idx - 10) % len(df)
                st.session_state.reveal = False
                st.rerun()

            if st.button("🏠 Auf Anfang"):
                st.session_state.idx = 0
                st.session_state.reveal = False
                st.rerun()
