import streamlit as st
import pandas as pd
import os

# --- KONFIGURATION & SESSION STATE ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100

st.sidebar.title("🎨 Design & Steuerung")

# Schriftgröße & Theme
st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)
themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme", list(themes.keys()))
t = themes[selected_theme]
scale = st.session_state.font_scale / 100.0

# --- DAS MAGISCHE CSS FÜR MOBILE SPALTEN ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    
    .card {{ 
        padding: {30 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.4 * scale}rem; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
/* DER MOBILE FIX: Spalten-Abstand und Breite */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important; /* Minimaler Abstand zwischen den Knöpfen */
        width: 100% !important;
    }}
    
    [data-testid="column"] {{
        flex: 1 !important;
        width: 48% !important; /* Fast die Hälfte */
        min-width: 0 !important; /* Verhindert das Herausschieben */
    }}

    .stButton > button {{
        width: 100% !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        white-space: nowrap !important; /* Verhindert Zeilenumbruch im Button */
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: {1.0 * scale}rem !important; /* Etwas kleiner auf Mobile */
    }}
    
    /* Speziell für den Text im Button */
    .stButton > button p {{
        font-size: 0.9rem !important;
        margin: 0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- LOGIK: DATEIEN LADEN ---
BASE_DIR = "Quizzes"
if not os.path.exists(BASE_DIR):
    st.info("Bitte erstelle einen Ordner namens 'Quizzes' in deinem Repo.")
else:
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    cat = st.sidebar.selectbox("Kategorie", categories)
    if cat:
        path = os.path.join(BASE_DIR, cat)
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        quiz = st.sidebar.selectbox("Quiz", files)
        
        if quiz:
            df = pd.read_csv(os.path.join(path, quiz))
            
            # Anzeige der Karte
            st.title(f"{cat}")
            q = df.iloc[st.session_state.idx, 0]
            a = df.iloc[st.session_state.idx, 1]
            
            st.markdown(f'<div class="card">{q}</div>', unsafe_allow_html=True)
            
            if st.button("Antwort anzeigen"):
                st.session_state.reveal = not st.session_state.reveal
            
            if st.session_state.reveal:
                st.info(f"**Antwort:** {a}")

            # Navigation
            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Zurück"):
                    st.session_state.idx = (st.session_state.idx - 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()
            with c2:
                if st.button("Weiter ➡️"):
                    st.session_state.idx = (st.session_state.idx + 1) % len(df)
                    st.session_state.reveal = False
                    st.rerun()
