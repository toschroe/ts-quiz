import streamlit as st
import pandas as pd
import os

# --- INITIALISIERUNG ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'reveal' not in st.session_state: st.session_state.reveal = False
if 'font_scale' not in st.session_state: st.session_state.font_scale = 100

# --- SIDEBAR & DESIGN ---
st.sidebar.title("🎨 Design & Steuerung")
st.session_state.font_scale = st.sidebar.slider("Schriftgröße (%)", 50, 150, st.session_state.font_scale, 5)

themes = {
    "Hell (NotebookLM)": {"bg": "#ffffff", "card_bg": "#fdfdfd", "text": "#1a1a1a", "border": "#eeeeee"},
    "Dunkel": {"bg": "#0e1117", "card_bg": "#1d2127", "text": "#fafafa", "border": "#31353f"},
    "Kontrast": {"bg": "#000000", "card_bg": "#000000", "text": "#ffff00", "border": "#ffff00"}
}
selected_theme = st.sidebar.selectbox("Theme", list(themes.keys()))
t = themes[selected_theme]
scale = st.session_state.font_scale / 100.0

# --- CSS: DER BRUTALE MOBILE FIX ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    
    /* Zwingt Spalten auf Mobile nebeneinander zu bleiben */
    [data-testid="column"] {{
        width: calc(50% - 5px) !important;
        flex: 1 1 calc(50% - 5px) !important;
        min-width: 0px !important;
    }}
    
    [data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 10px !important;
    }}

    /* Container Padding oben/unten */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }}

    /* Card & Text */
    .card {{ 
        padding: {25 * scale}px; border-radius: 20px; 
        background: {t['card_bg']}; color: {t['text']};
        border: 2px solid {t['border']}; text-align: center; 
        font-size: {1.3 * scale}rem; margin-top: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}

    .stButton > button {{
        width: 100% !important; border-radius: 12px;
        border: 1px solid {t['border']} !important;
        background-color: {t['card_bg']} !important;
        color: {t['text']} !important;
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
        quiz = st.sidebar.selectbox("Quiz", files)
        
        if quiz:
            df = pd.read_csv(os.path.join(path, quiz))
            
            # Fortschrittsbalken
            progress = (st.session_state.idx + 1) / len(df)
            st.progress(progress)
            st.caption(f"Frage {st.session_state.idx + 1} von {len(df)}")

            # Navigation oben
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

            # Quiz-Inhalt
            q = df.iloc[st.session_state.idx, 0]
            a = df.iloc[st.session_state.idx, 1]
            st.markdown(f'<div class="card">{q}</div>', unsafe_allow_html=True)
            
            if st.button("Antwort prüfen"):
                st.session_state.reveal = not st.session_state.reveal
            
            if st.session_state.reveal:
                st.info(f"**Antwort:** {a}")
