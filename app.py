import streamlit as st
import pandas as pd
import os
import random

# --- INITIALISIERUNG ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100
if 'order' not in st.session_state: st.session_state.order = []
if 'last_quiz' not in st.session_state: st.session_state.last_quiz = ""

# --- SIDEBAR: DESIGN & LOGIK ---
st.sidebar.title("🎨 Design & Logik")

# Theme-Definitionen
themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "sidebar": "#f8f9fa", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "sidebar": "#161b22", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "sidebar": "#1a1a00", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme wählen", list(themes.keys()))
t = themes[selected_theme]

# Shuffle-Steuerung
shuffle_mode = st.sidebar.checkbox("Zufällige Reihenfolge", value=False)
if st.sidebar.button("🎲 Neu Mischen"):
    st.session_state.order = [] # Erzwingt Neu-Generierung
    st.session_state.idx = 0
    st.rerun()

st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)
scale = st.session_state.font_scale / 100.0

# --- CSS: VOLLSTÄNDIGE INTEGRATION ---
st.markdown(f"""
    <style>
    /* Haupt-App & Sidebar Hintergrund */
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    [data-testid="stSidebar"] {{ 
        background-color: {t['sidebar']} !important; 
        border-right: 1px solid {t['border']};
    }}
    
    /* Text-Farben in der Sidebar erzwingen */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {{ 
        color: {t['text']} !important; 
    }}

    /* Container-Abstände */
    [data-testid="stAppViewBlockContainer"] {{ 
        padding-top: 2rem !important; 
        padding-bottom: 6rem !important; 
    }}

    /* Die Karte */
    .card {{ 
        padding: {25 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.3 * scale}rem; margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        min-height: 180px;
        display: flex; align-items: center; justify-content: center;
    }}

    /* Button-Design (Main & Sidebar) */
    .stButton > button {{
        width: 100% !important; border-radius: 12px !important;
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important;
        height: 3.5em !important;
        margin-bottom: 5px !important;
    }}
    
    /* Verhindert das Verschwinden der Header-Icons */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    header[data-testid="stHeader"] svg {{
        fill: {t['text']} !important;
    }}

    .stMarkdown, p, span, label, .stCaption {{ color: {t['text']} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- INHALT LADEN ---
BASE_DIR = "Quizzes"
if os.path.exists(BASE_DIR):
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    cat = st.sidebar.selectbox("Kategorie", categories)
    if cat:
        path = os.path.join(BASE_DIR, cat)
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        quiz_file = st.sidebar.selectbox("Quiz", files)
        
        if quiz_file:
            # Dateiname ohne Endung für die Button-Beschriftung
            quiz_name_clean = os.path.splitext(quiz_file)[0].replace('_', ' ')
            
            # Daten laden
            df = pd.read_csv(os.path.join(path, quiz_file))
            num_cards = len(df)

            # Reset bei Quiz-Wechsel oder leerer Order
            if st.session_state.last_quiz != quiz_file or not st.session_state.order or len(st.session_state.order) != num_cards:
                st.session_state.order = list(range(num_cards))
                if shuffle_mode:
                    random.shuffle(st.session_state.order)
                st.session_state.idx = 0
                st.session_state.last_quiz = quiz_file
                st.rerun()
            
            # Fortschritt
            progress_val = (st.session_state.idx + 1) / num_cards
            st.progress(progress_val)
            st.caption(f"Karte {st.session_state.idx + 1} von {num_cards}")

            # 1. NAVIGATION OBEN
            if st.button(f"Weiter mit {quiz_name_clean} ➡️"):
                st.session_state.idx = (st.session_state.idx + 1) % num_cards
                st.session_state.reveal = False
                st.rerun()

            # 2. FRAGE
            current_row = st.session_state.order[st.session_state.idx]
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
                st.session_state.idx = (st.session_state.idx - 1) % num_cards
                st.session_state.reveal = False
                st.rerun()
            
            if st.button("⏪ 10 Karten zurück"):
                st.session_state.idx = (st.session_state.idx - 10) % num_cards
                st.session_state.reveal = False
                st.rerun()

            if st.button("🏠 Auf Anfang"):
                st.session_state.idx = 0
                st.session_state.reveal = False
                st.rerun()
else:
    st.warning("Ordner 'Quizzes' nicht gefunden.")
